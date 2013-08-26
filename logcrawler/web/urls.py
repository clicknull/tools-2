#coding: UTF-8
from django.conf.urls import patterns, include, url

# from application import api, views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # -- REST INTERFACE --
    # idc配置
    url(r'^IDC_collect/get/$', "application.api.idcs.get", name="idcs_get"),
    url(r'^IDC_collect/create/$', "application.api.idcs.create", name="idcs_create"),
    url(r'^IDC_collect/delete/$', "application.api.idcs.delete", name="idcs_delete"),
    url(r'^IDC_collect/update/$', "application.api.idcs.update", name="idcs_update"),
    url(r'^IDC_collect/getoptions/$', "application.api.idcs.getoptions", name="idcs_getoptions"),

    # analyze规则配置
    url(r'^analyze_process_rules/get/$', "application.api.analyze_rules.get", name="analyze_rules_get"),
    url(r'^analyze_process_rules/create/$', "application.api.analyze_rules.create", name="analyze_rules_create"),
    url(r'^analyze_process_rules/delete/$', "application.api.analyze_rules.delete", name="analyze_rules_delete"),
    url(r'^analyze_process_rules/update/$', "application.api.analyze_rules.update", name="analyze_rules_update"),
    url(r'^analyze_process_rules/getoptions/$', "application.api.analyze_rules.getoptions", name="analyze_rules_getoptions"),

    # regexp verification 前向验证
    url(r'^regexp_verification/get/$', "application.api.analyze_rules.verify_get", name="analyze_verify_get"),
    url(r'^regexp_verification/create/$', "application.api.analyze_rules.verify_create", name="analyze_verify_create"),

    # download监控
    url(r'^download/get/$', "application.api.crawl_stats.get", name="crawl_stats_get"),
    url(r'^download/create/$', "application.api.crawl_stats.create", name="crawl_stats_create"),
    url(r'^download/delete/$', "application.api.crawl_stats.delete", name="crawl_stats_delete"),
    url(r'^download/update/$', "application.api.crawl_stats.update", name="crawl_stats_update"),

    # analyze监控
    url(r'^analyze/get/$', "application.api.analyze_stats.get", name="analyze_stats_get"),
    url(r'^analyze/create/$', "application.api.analyze_stats.create", name="analyze_stats_create"),
    url(r'^analyze/delete/$', "application.api.analyze_stats.delete", name="analyze_stats_delete"),
    url(r'^analyze/update/$', "application.api.analyze_stats.update", name="analyze_stats_update"),

    # -- WEB PAGE --
    url(r'^console/crawl/$', "application.views.home.crawl", name="console_crawl"),
    url(r'^console/idc/$', "application.views.home.config_idc", name="console_idc"),
    url(r'^console/analyze/$', "application.views.home.analyze", name="console_analyze"),
    url(r'^rules/$', "application.views.home.home", name="rules"),

    # -------------------- for new REST interface --------------------
    # url(r'^analyze/rules/$', api.analyze_rules.AnalyzeRulesView.as_view(), name="analyze_rules"),
    # url(r'^analyze/status/$', api.analyze_stats.AnalyzeStatsView.as_view(), name="analyze_status"),
    # url(r'^idc/config/$', api.idcs.IDCView.as_view(), name="idc_config"),
    # url(r'^crawl/status/$', api.crawl_stats.CrawlStatsView.as_view(), name="crawl_status"),

    # Examples:
    # url(r'^$', 'rest.views.home', name='home'),
    # url(r'^rest/', include('rest.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
