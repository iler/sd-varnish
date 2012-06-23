import subprocess

from xml.etree import ElementTree

class Varnishstat(object):
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig
    
    def run(self):
        stats = {}
        varnishstat = subprocess.Popen(
            ['varnishstat','-x'],
            stdout=subprocess.PIPE,
        )
        stats_xml = ElementTree.parse(varnishstat.stdout)
        
        for stat_node in stats_xml.findall('stat'):
          label = stat_node.findtext('description')
          value = stat_node.findtext('value')
          stats[label] = value
	
	# Count uptime in days
	uptime = float(stats['Client uptime'])
        stats['Client uptime'] = uptime / 86400

	requests_new = int(stats['Client requests received'])
        hits_new = int(stats['Cache hits'])
        misses_new = int(stats['Cache misses'])
        requests_old = int(0)
        hits_old = int(0)
        misses_old = int(0)
        
        try:
          with open('/tmp/sdstats', 'r') as sfile:
            requests_old = int(sfile.readline())
            hits_old = int(sfile.readline())
            misses_old = int(sfile.readline())
            sfile.close()        
        except IOError as e:
          sfile = open('/tmp/sdstats', 'w')
          req = str(requests_new)
          hit = str(hits_new)
          miss = str(misses_new)
          sfile.write(req + '\n' + hit + '\n' + miss)
          sfile.close()
          
        sfile = open('/tmp/sdstats', 'w')
        req = str(requests_new)
        hit = str(hits_new)
        miss = str(misses_new)
        sfile.write(req + '\n' + hit + '\n' + miss)
        sfile.close()
          
        requests = float(requests_new - requests_old)
        hits = float(hits_new - hits_old)
        misses = float(misses_new - misses_old)
        if requests != 0.00:
          stats['Hit ratio'] = float(hits / requests) * 100
          stats['Miss ratio'] = float(misses / requests) * 100
          stats['Client requests received'] = int(requests)
          stats['Cache hits'] = int(hits)
          stats['Cache misses'] = int(misses)
        else:
          stats['Hit ratio'] = 0.00
          stats['Miss ratio'] = 0.00
          stats['Client requests received'] = 0
          stats['Cache hits'] = 0
          stats['Cache misses'] = 0
        
        # Convert body and header bytes to MB
        body_bytes = float(stats['Total body bytes'])
	stats['Total body MB'] = float(body_bytes / 1048576)
	header_bytes = float(stats['Total header bytes'])
	stats['Total header MB'] = float(header_bytes / 1048576)
        
        return stats
