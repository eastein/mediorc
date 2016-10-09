from __future__ import absolute_import
import time
import dns.resolver

class ResolverCacher(object) :
	def __init__(self) :
		self.cache = dict()

	# not thread safe
	# TODO add negative result caching?
	def query(self, name, t) :
		if (name, t) in self.cache :
			result = self.cache[(name, t)]
			if time.time() < result.expiration :
				return result
			else :
				del self.cache[(name, t)]

		result = dns.resolver.query(name, t)
		self.cache[(name, t)] = result
		return result

	def all_ips(self, name) :
		results = list()
		for t in ['A', 'AAAA'] :
			try :
				results.append(self.query(name, t))
			except dns.exception.DNSException :
				pass

		r = list()
		for resultset in results :
			for result in resultset :
				r.append(result.to_text())
		return r
