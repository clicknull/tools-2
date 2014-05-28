#!/usr/bin/env python
# coding: utf-8

from django.shortcuts import render_to_response

def home(request):
    tag = "rules"
    title = u"分析规则配置接口"
    source = "/_logcrawler/logcrawler_rest_api/analyze_process_rules/get/"
    # source = "/analyze_process_rules/get/"
    theaders = ["HOST - IP - SERVICE", "REGEXP", "ACTION", "PARAM", "STATUS", "TIME"]

    return render_to_response("custom_table.html", locals())

    
def crawl(request):
    tag = "crawl"
    title = u"网络爬虫下载监控"
    source = "/_logcrawler/logcrawler_rest_api/download/get/"
    # source = "/download/get/"
    theaders = ["WORKER", "URL", "STARTTIME", "SIZE", "SPEND", "SPEED", "STATUS", "DETAIL"]

    return render_to_response("table.html", locals())

def analyze(request):
    tag = "analyze"
    title = u"网络爬虫分析监控"
    source = "/_logcrawler/logcrawler_rest_api/analyze/get/"
    # source = "/analyze/get/"
    theaders = ["WORKER", "FILE", "LINES", "SIZE", "START", "END", "SPEND", "STATUS", "DETAIL"]

    return render_to_response("table.html", locals())

def config_idc(request):
    tag   = "idc"
    title = u"采集机房配置接口"
    # source = "/IDC_collect/get/"
    source      = "/_logcrawler/logcrawler_rest_api/IDC_collect/get/"
    theaders    = ["HOST", "IP", "DESCRIPTION", "SERVICE", "INTERVAL",
                   "DELAY", "MAX DELAY", "STATUS", "HEARTBEAT", "TIME"]

    return render_to_response("custom_table.html", locals())
