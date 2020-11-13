# -*- coding: utf-8 -*-

import os
import sys
import math
import random
import collections
from operator import itemgetter
from collections import defaultdict

class LFM(object):
    '''
    LFM model
    '''

    def __init__(self, F, step, alpha, lamb, n_rec_movie=10):
        '''
        init LFM with F,step,alpha,lamb,n_rec_movie
        :param F:隐特征的个数
        :param step:步数
        :param alpha:学习率
        :param lamb:正则化参数
        :param n_rec_movie:推荐电影数
        '''
        self.F = F
        self.step = step
        self.alpha = alpha
        self.lamb = lamb
        self.n_rec_movie = n_rec_movie
        self.users_set, self.items_set = set(), set()
        self.items_list = list()
        self.P, self.Q = None, None
        self.trainset = None
        self.testset = None
        self.item_popular, self.items_count = None, None

    def init_model(self, users_set, items_set, F):
        '''
        init model,set P and Q with random numbers
        :param users_set:用户集
        :param items_set:物品集
        :param F:隐特征的个数
        :return:None
        '''
        self.P = dict()
        self.Q = dict()
        for user in users_set:
            self.P[user] = [random.random()/math.sqrt(F) for _ in range(F)]
        for item in items_set:
            self.Q[item] = [random.random()/math.sqrt(F) for _ in range(F)]

    def init_users_items_set(self, trainset):
        """
        Get users set and items set.
        :param trainset: 训练集
        :return: 基础的用户和物品集合
        """
        users_set, items_set = set(), set()
        items_list = []
        item_popular = defaultdict(int)
        for user, movies in trainset.items():
            for item in movies:
                item_popular[item] += 1
                users_set.add(user)
                items_set.add(item)
                items_list.append(item)
        items_count = len(items_set)
        return users_set, items_set, items_list, item_popular, items_count

    def generate_negative_sample(self, items: dict):
        """
        Generate negative samples
        :param items: 原始物品（正样本）
        :return: 正样本和负样本
        """
        samples = dict()
        for item, rate in items.items():
            samples[item] = 1
        for i in range(len(items) * 11):
            item = self.items_list[random.randint(0, len(self.items_list) - 1)]
            if item in samples:
                continue
            samples[item] = 0
            if len(samples) >= 10 * len(items):
                break
        return samples

    def predict(self, user, item):
        '''
        predict the rate for item given user and P and Q.
        :param user:用户
        :param item:物品
        :return:预测概率
        '''
        rate = 0
        for f in range(self.F):
            p = self.P[user][f]
            q = self.Q[item][f]
            rate += p*q
        return rate

    def train(self, trainset):
        '''
        train model.
        :param trainset: 训练集
        :return: None
        '''
        self.trainset = trainset
        #模型评估相关参数
        self.users_set, self.items_set, self.items_list, self.item_popular, self.items_count = \
            self.init_users_items_set(trainset)
        #p,q初始化
        self.init_model(self.users_set, self.items_set, self.F)
        for step in range(self.step):
            print('step:', step)
            for user in trainset:
                samples = self.generate_negative_sample(trainset[user])
                for item, rui in samples.items():
                    eui = rui - self.predict(user, item)
                    for f in range(self.F):
                        self.P[user][f] += self.alpha * (eui * self.Q[item][f] - self.lamb * self.P[user][f])
                        self.Q[item][f] += self.alpha * (eui * self.P[user][f] - self.lamb * self.Q[item][f])
            self.alpha *= 0.9#随机梯度下降

    def recommend(self, user):
        """
        Recommend N movies for the user.
        :param user: The user we recommend movies to.
        :return: the N best score movies
        """
        rank = collections.defaultdict(float)
        interacted_items = self.trainset[user]
        for item in self.items_set:
            if item in interacted_items.keys():
                continue
            for k, Qik in enumerate(self.Q[item]):
                rank[item] += self.P[user][k] * Qik
        return [movie for movie, _ in sorted(rank.items(), key=itemgetter(1), reverse=True)][:self.n_rec_movie]

    def test(self, testset):
        """
        Test the recommendation system by recommending scores to all users in testset.
        :param testset: test dataset
        :return: None
        """
        self.testset = testset
        print('Test recommendation system start...')
        #  varables for precision and recall
        hit = 0
        rec_count = 0
        test_count = 0
        # varables for coverage
        all_rec_movies = set()
        # varables for popularity
        popular_sum = 0

        # record the calculate time has spent.
        for user in self.users_set:
            test_movies = self.testset.get(user, {})
            rec_movies = self.recommend(user)  # type:list
            for movie in rec_movies:
                if movie in test_movies.keys():
                    hit += 1
                all_rec_movies.add(movie)
                popular_sum += math.log(1 + self.item_popular[movie])
                # log steps and times.
            rec_count += self.n_rec_movie
            test_count += len(test_movies)
        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * self.items_count)
        popularity = popular_sum / (1.0 * rec_count)
        print('Test recommendation system success.')
        print('precision=%.4f\trecall=%.4f\tcoverage=%.4f\tpopularity=%.4f\n' %
              (precision, recall, coverage, popularity))

def recommend_test(model, user_list):
    for user in user_list:
        recommend = model.recommend(str(user))
        print("recommend for userid = %s:" % user)
        print(recommend)
        print()

def loadfile(filename):
    ''' load a file, return a generator. '''
    fp = open(filename, 'r')
    for i, line in enumerate(fp):
        yield line.strip('\r\n')
        if i % 100000 == 0:
            print ('loading %s(%s)' % (filename, i), file=sys.stderr)
    fp.close()
    print ('load %s successfully' % filename, file=sys.stderr)

def get_dataset(filename, pivot=0.7):
    ''' load rating data and split it to training set and test set '''
    trainset_len = 0
    testset_len = 0
    trainset = {}
    testset = {}

    for line in loadfile(filename):
        user, movie, rating, _ = line.split('::')
        # split the data by pivot
        if random.random() < pivot:
            trainset.setdefault(user, {})
            trainset[user][movie] = int(rating)
            trainset_len += 1
        else:
            testset.setdefault(user, {})
            testset[user][movie] = int(rating)
            testset_len += 1

    print ('split training set and test set successfully', file=sys.stderr)
    print ('train set = %s' % trainset_len, file=sys.stderr)
    print ('test set = %s' % testset_len, file=sys.stderr)

    return trainset,testset

if __name__ == '__main__':
    lfm = LFM(10, 20, 0.1, 0.01, 10)
    filename = os.path.join('dat', 'ratings.dat')
    trainset,testset = get_dataset(filename)
    lfm.train(trainset)
    recommend_test(lfm,[11, 155, 208, 399, 571,1020])
    lfm.test(testset)
