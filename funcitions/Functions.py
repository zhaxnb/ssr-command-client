from utils.InitUtils import *
from utils.HandleSSRUtils import *
from utils.PrintUtils import *
from utils.SSRTestUtils import *
from utils.SettingUtils import *
from utils.ParseUtils import *

i = InitConfigDir()
settings = Setting(i.configFilePath)
u = UpdateSubscribeUrl(i.ssrListJsonFile, settings.valueDict['subscribe_url'])
h = ControlSSR()
ssrTable = DrawInfoListTable()

def isIDValid(func):
    def judge(*args, **kwargs):
        if kwargs['id'] < 0 or kwargs['id'] >= len(u.ssrInfoList):
            logger.error('ssr id error')
            sys.exit(1)
        else:
            ssrLogger.addHandler(streamHandler)
            func(*args, **kwargs)
            ssrLogger.removeFilter(streamHandler)
    return judge


class Hanlder(object):

    def __init__(self):
        pass

    @isIDValid
    def start(self, id, port=1080):
        if i.platform == 'win32':
            h.startOnWindows(u.ssrInfoList[id], settings.local_address,
                             port,
                             settings.timeout,
                             settings.workers)
        else:
            h.startOnUnix(u.ssrInfoList[id], settings.local_address,
                          port,
                          settings.timeout,
                          settings.workers,
                          i.pidFilePath,
                          i.logFilePath)

    @isIDValid
    def stop(self, id, port=1080):
        h.stopOnUnix(u.ssrInfoList[id], settings.local_address,
                      port,
                      settings.timeout,
                      settings.workers,
                      i.pidFilePath,
                      i.logFilePath)
        os.remove(i.pidFilePath)

    def startFastNode(self):
        pingList = list()
        for ssrInfo in u.ssrInfoList:
            if ssrInfo['ping'] == '∞':
                ping = 10000
            else:
                ping = float(ssrInfo['ping'])
            pingList.append(ping)
        index = pingList.index(min(pingList))
        logger.info("select fast node {0} ping {1}ms".
                    format(u.ssrInfoList[index]['remarks'], pingList[index]))
        self.start(id=index)

class Update(object):

    def __init__(self):
        pass

    def updateSubscribe(self):
        ssrInfoList = u.update(i.ssrListJsonFile,
                               settings.valueDict['subscribe_url'].split('|'))
        ssrInfoList = s.startConnectTest(ssrInfoList)
        u.updateCacheJson(i.ssrListJsonFile, ssrInfoList)
        u.ssrInfoList = ssrInfoList

    def updateSubcribeUrl(self, url):
        settings.setValue('subscribe_url', url)
        logger.info('change subscribe url to: {0}'.format(url))

    def updateLocalAddress(self, address):
        settings.setValue('local_address', address)
        logger.info('change subscribe url to: {0}'.format(address))



class Display(object):

    def __init__(self):
        pass

    def displaySSRList(self):
        for ssrInfo in u.ssrInfoList:
            ssrTable.append(
                id=ssrInfo['id'],
                name=ssrInfo['remarks'],
                ping=ssrInfo['ping'],
                connect=ssrInfo['connect'],
                server=ssrInfo['server'],
                port=ssrInfo['server_port'],
                method=ssrInfo['method']
            )
        ssrTable.print()

    def displaySSRSpeedList(self):
        pass

    def displaySuscribeUrl(self):
        for url in u.urlList:
            color.print(url, 'blue')

    def displayLocalAddress(self):
        color.print(settings.valueDict['local_address'],
                    'blue')

    def displaySSRJson(self, id):
        color.print(json.dumps(u.ssrInfoList[id], ensure_ascii=False, indent=4),
                    'yellow')

    def parseSSRUrl(self, ssrUrl):
        ssrInfo = ParseShadowsocksR.parseShadowsocksR(ssrUrl)
        ssrInfo = s.testSSRConnect(ssrInfo)
        color.print(json.dumps(ssrInfo, ensure_ascii=False, indent=4),
                    'yellow')