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

	# Count cache hit and miss ratios
	requests = float(stats['Client requests received'])
        hits = float(stats['Cache hits'])
        misses = float(stats['Cache misses'])
        stats['Hit ratio'] = float(hits / requests) * 100
        stats['Miss ratio'] = float(misses / requests) * 100
        
        # Convert body and header bytes to MB
        body_bytes = float(stats['Total body bytes'])
	stats['Total body MB'] = float(body_bytes / 1048576)
	header_bytes = float(stats['Total header bytes'])
	stats['Total header MB'] = float(header_bytes / 1048576)
        
        return stats
