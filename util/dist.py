# -*- coding:utf-8 -*-
# Módulo que calcula os tempos entre chegadas de um distribuição exponencial


import math
import random
import estimator


def exp_time(rate):
	"""Retorna um tempo aleatório de uma distribuição exponencial com taxa [rate]."""
	return -(math.log(1.0 - random.random())/rate)
	
if __name__ == "__main__":
	print "Testando..."
	print estimator.mean(exp_time(2, 650))