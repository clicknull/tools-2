#coding: UTF-8
from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns

from application import api, views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # -- REST INTERFACE --
    # idc配置
    url(r'^IDC_collect/get/$', "application.api.idcs.oldget", name="idcs_get"),
    url(r'^IDC_collect/create/$', "application.api.idcs.oldcreate", name="idcs_create"),
    url(r'^IDC_collect/delete/$', "application.api.idcs.olddelete", name="idcs_delete"),
    url(r'^IDC_collect/update/$', "application.api.idcs.oldupdate", name="idcs_update"),
    url(r'^IDC_collect/getoptions/$', "application.api.idcs.oldgetoptions", name="idcs_getoptions"),

    # analyze规则配置
    url(r'^analyze_process_rules/get/$', "application.api.analyze_rules.oldget", name="analyze_rules_get"),
    url(r'^analyze_process_rules/create/$', "application.api.analyze_rules.oldcreate", name="analyze_rules_create"),
    url(r'^analyze_process_rules/delete/$', "application.api.analyze_rules.olddelete", name="analyze_rules_delete"),
    url(r'^analyze_process_rules/update/$', "application.api.analyze_rules.oldupdate", name="analyze_rules_update"),
    url(r'^analyze_process_rules/getoptions/$', "application.api.analyze_rules.oldgetoptions", name="analyze_rules_getoptions"),

    # regexp verification 前向验证
    url(r'^regexp_verification/get/$', "application.api.analyze_rules.verify_get", name="analyze_verify_get"),
    url(r'^regexp_verification/create/$', "application.api.analyze_rules.verify_create", name="analyze_verify_create"),

    # download监控
    url(r'^download/get/$', "application.api.crawl_stats.oldget", name="crawl_stats_get"),
    url(r'^download/create/$', "application.api.crawl_stats.oldcreate", name="crawl_stats_create"),
    url(r'^download/delete/$', "application.api.crawl_stats.olddelete", name="crawl_stats_delete"),
    url(r'^download/update/$', "application.api.crawl_stats.oldupdate", name="crawl_stats_update"),

    # analyze监控
    url(r'^analyze/get/$', "application.api.analyze_stats.oldget", name="analyze_stats_get"),
    url(r'^analyze/create/$', "application.api.analyze_stats.oldcreate", name="analyze_stats_create"),
    url(r'^analyze/delete/$', "application.api.analyze_stats.olddelete", name="analyze_stats_delete"),
    url(r'^analyze/update/$', "application.api.analyze_stats.oldupdate", name="analyze_stats_update"),

    # -- WEB PAGE --
    url(r'^console/crawl/$', "application.views.home.crawl", name="console_crawl"),
    url(r'^console/idc/$', "application.views.home.config_idc", name="console_idc"),
    url(r'^console/analyze/$', "application.views.home.analyze", name="console_analyze"),
    url(r'^rules/$', "application.views.home.home", name="rules"),

    # --
    # -------------------- for new REST interface --------------------
    # --
    ##url(r'^downloader/status$', api.crawl_stats.CrawlStatuses.as_view()),
    # url(r'^downloader/config$', api.idcs.IDCConfigs.as_view()),
    # url(r'^analyzer/status$', api.analyze_stats.AnalyzeStatuses.as_view()),
    # url(r'^analyzer/config$', api.analyze_rules.AnalyzeRules.as_view()),

    ##url(r'^downloader/status/show$', api.crawl_stats.show),
    ##url(r'^downloader/status/create$', api.crawl_stats.create),
    ##url(r'^downloader/status/update$', api.crawl_stats.update),
    ##url(r'^downloader/status/destroy$', api.crawl_stats.destroy),
    # url(r'^downloader/status/show/(?P<id>[0-9]+)$', "application.api.crawl_stats.get"),
    # url(r'^downloader/status/create/(?P<id>[0-9]+)$', "application.api.crawl_stats.create"),
    # url(r'^downloader/status/update/(?P<id>[0-9]+)$', "application.api.crawl_stats.update"),
    # url(r'^downloader/status/destroy/(?P<id>[0-9]+)$', "application.api.crawl_stats.delete"),


    # Examples:
    # url(r'^$', 'rest.views.home', name='home'),
    # url(r'^rest/', include('rest.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns = format_suffix_patterns(urlpatterns)
