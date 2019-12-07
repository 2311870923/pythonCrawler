from selenium import webdriver
from selenium.webdriver import ChromeOptions
import os, requests, sys, csv, time, random, threading

options = ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
desired_capabilities = options.to_capabilities()
desired_capabilities['acceptSslCerts'] = True
desired_capabilities['acceptInsecureCerts'] = True

cookies_str = '_lxsdk_cuid=1688917eef6c8-06a15647cde66a-10376655-1fa400-1688917eef7c8; _lxsdk=1688917eef6c8-06a15647cde66a-10376655-1fa400-1688917eef7c8; _hc.v=9d734ecb-8555-47f6-8acc-ca8c2045ba5b.1548488274; s_ViewType=10; aburl=1; _dp.ac.v=10fac4a2-5ee4-438c-9b30-f00de3e64c4c; dper=3a5731b742657415f5ec517cee0d2fb49b800de9def0c30bb51b6dc740802c2ae75a87ab41327859ab8685b6edcfc69a936f49f714250439b928d0b731ee6aa0438752ac75caa3a1be8b531e2534a52dce68c6d1c1f8b292fe96a43a825ab56c; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_8571880941; ctu=50ed51cf16794a23e2466c4af4c57865ce740eca1190a2af950e3b53383d3aa7; uamo=15737135239; Hm_lvt_dbeeb675516927da776beeb1d9802bd4=1554723400,1555208290; cy=2; cye=beijing; Hm_lpvt_dbeeb675516927da776beeb1d9802bd4=1555208340; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=16a2a4880da-32d-623-c55%7C%7C60'
cookies = {i.split('=')[0]: i.split('=')[1] for i in cookies_str.split('; ')}

driver = webdriver.Chrome(executable_path="/Users/echo/Documents/sites/wxhub-master/chromedriver", options=options,
                          desired_capabilities=desired_capabilities)

time.sleep(1000000)