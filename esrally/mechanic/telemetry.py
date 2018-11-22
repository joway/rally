import collections
import logging
import os
import re
import signal
import subprocess
import tabulate
import threading
import json

from esrally import metrics, time, exceptions
from esrally.utils import io, sysstats, console, versions, opts
from esrally.metrics import MetaInfoScope

MOCK_NODE_INFO = json.loads("""
{
  "_nodes": {
    "total": 4,
    "successful": 4,
    "failed": 0
  },
  "cluster_name": "elasticsearch-cluster",
  "nodes": {
    "KmbJ-gnWTCO7I5oemlQIgw": {
      "timestamp": 1542866602045,
      "name": "elasticsearch-2",
      "transport_address": "10.56.9.5:9300",
      "host": "10.56.9.5",
      "ip": "10.56.9.5:9300",
      "roles": [
        "master",
        "data",
        "ingest"
      ],
      "attributes": {
        "ml.machine_memory": "26843545600",
        "ml.max_open_jobs": "20",
        "xpack.installed": "true",
        "ml.enabled": "true"
      },
      "indices": {
        "docs": {
          "count": 1518363451,
          "deleted": 1444
        },
        "store": {
          "size_in_bytes": 733610863579
        },
        "indexing": {
          "index_total": 1856686601,
          "index_time_in_millis": 380053688,
          "index_current": 0,
          "index_failed": 0,
          "delete_total": 0,
          "delete_time_in_millis": 0,
          "delete_current": 0,
          "noop_update_total": 0,
          "is_throttled": false,
          "throttle_time_in_millis": 0
        },
        "get": {
          "total": 23643,
          "time_in_millis": 2032,
          "exists_total": 11784,
          "exists_time_in_millis": 998,
          "missing_total": 11859,
          "missing_time_in_millis": 1034,
          "current": 0
        },
        "search": {
          "open_contexts": 0,
          "query_total": 164817,
          "query_time_in_millis": 8226703,
          "query_current": 0,
          "fetch_total": 84514,
          "fetch_time_in_millis": 12304,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 3,
          "current_docs": 12331667,
          "current_size_in_bytes": 5545551873,
          "total": 55956,
          "total_time_in_millis": 970932305,
          "total_docs": 5731001877,
          "total_size_in_bytes": 3324300715866,
          "total_stopped_time_in_millis": 141088,
          "total_throttled_time_in_millis": 743188540,
          "total_auto_throttle_in_bytes": 714240478
        },
        "refresh": {
          "total": 307906,
          "total_time_in_millis": 74075173,
          "listeners": 0
        },
        "flush": {
          "total": 4478,
          "periodic": 4437,
          "total_time_in_millis": 4641422
        },
        "warmer": {
          "current": 0,
          "total": 276641,
          "total_time_in_millis": 61034
        },
        "query_cache": {
          "memory_size_in_bytes": 108686617,
          "total_count": 189361,
          "hit_count": 87968,
          "miss_count": 101393,
          "cache_size": 286,
          "cache_count": 637,
          "evictions": 351
        },
        "fielddata": {
          "memory_size_in_bytes": 920,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 753,
          "memory_in_bytes": 1653546141,
          "terms_memory_in_bytes": 1322253388,
          "stored_fields_memory_in_bytes": 291019056,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 1216,
          "points_memory_in_bytes": 34349149,
          "doc_values_memory_in_bytes": 5923332,
          "index_writer_memory_in_bytes": 98973392,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542861071320,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 5997850,
          "size_in_bytes": 6410552281,
          "uncommitted_operations": 2519240,
          "uncommitted_size_in_bytes": 2162674779,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 848,
          "evictions": 0,
          "hit_count": 27715,
          "miss_count": 1409
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 7614
        }
      },
      "os": {
        "timestamp": 1542866602103,
        "cpu": {
          "percent": 31,
          "load_average": {
            "1m": 3.58,
            "5m": 2.89,
            "15m": 2.76
          }
        },
        "mem": {
          "total_in_bytes": 31629697024,
          "free_in_bytes": 603795456,
          "used_in_bytes": 31025901568,
          "free_percent": 2,
          "used_percent": 98
        },
        "swap": {
          "total_in_bytes": 0,
          "free_in_bytes": 0,
          "used_in_bytes": 0
        },
        "cgroup": {
          "cpuacct": {
            "control_group": "/",
            "usage_nanos": 693266882847980
          },
          "cpu": {
            "control_group": "/",
            "cfs_period_micros": 100000,
            "cfs_quota_micros": -1,
            "stat": {
              "number_of_elapsed_periods": 0,
              "number_of_times_throttled": 0,
              "time_throttled_nanos": 0
            }
          },
          "memory": {
            "control_group": "/",
            "limit_in_bytes": "26843545600",
            "usage_in_bytes": "26843402240"
          }
        }
      },
      "process": {
        "timestamp": 1542866602103,
        "open_file_descriptors": 605,
        "max_file_descriptors": 1048576,
        "cpu": {
          "percent": 30,
          "total_in_millis": 693240540
        },
        "mem": {
          "total_virtual_in_bytes": 748899540992
        }
      },
      "jvm": {
        "timestamp": 1542866602104,
        "uptime_in_millis": 233790101,
        "mem": {
          "heap_used_in_bytes": 6041378200,
          "heap_used_percent": 47,
          "heap_committed_in_bytes": 12823887872,
          "heap_max_in_bytes": 12823887872,
          "non_heap_used_in_bytes": 157013104,
          "non_heap_committed_in_bytes": 190812160,
          "pools": {
            "young": {
              "used_in_bytes": 430108000,
              "max_in_bytes": 488636416,
              "peak_used_in_bytes": 488636416,
              "peak_max_in_bytes": 488636416
            },
            "survivor": {
              "used_in_bytes": 42065216,
              "max_in_bytes": 61014016,
              "peak_used_in_bytes": 61014016,
              "peak_max_in_bytes": 61014016
            },
            "old": {
              "used_in_bytes": 5569306736,
              "max_in_bytes": 12274237440,
              "peak_used_in_bytes": 9584214728,
              "peak_max_in_bytes": 12274237440
            }
          }
        },
        "threads": {
          "count": 108,
          "peak_count": 121
        },
        "gc": {
          "collectors": {
            "young": {
              "collection_count": 297912,
              "collection_time_in_millis": 9367443
            },
            "old": {
              "collection_count": 15257,
              "collection_time_in_millis": 784543
            }
          }
        },
        "buffer_pools": {
          "mapped": {
            "count": 1853,
            "used_in_bytes": 729458194901,
            "total_capacity_in_bytes": 729458194901
          },
          "direct": {
            "count": 91,
            "used_in_bytes": 237993475,
            "total_capacity_in_bytes": 237993474
          }
        },
        "classes": {
          "current_loaded_count": 17662,
          "total_loaded_count": 17916,
          "total_unloaded_count": 254
        }
      },
      "thread_pool": {
        "analyze": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ccr": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "fetch_shard_started": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 12,
          "completed": 20
        },
        "fetch_shard_store": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 8,
          "completed": 34
        },
        "flush": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 35385
        },
        "force_merge": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 1,
          "completed": 4
        },
        "generic": {
          "threads": 6,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 6,
          "completed": 978040
        },
        "get": {
          "threads": 7,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 7,
          "completed": 23643
        },
        "index": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "listener": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "management": {
          "threads": 5,
          "queue": 0,
          "active": 1,
          "rejected": 0,
          "largest": 5,
          "completed": 816841
        },
        "ml_autodetect": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ml_datafeed": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ml_utility": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "refresh": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 2717186
        },
        "rollup_indexing": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "search": {
          "threads": 11,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 11,
          "completed": 208691
        },
        "search_throttled": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "security-token-key": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "snapshot": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "warmer": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 202484
        },
        "watcher": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "write": {
          "threads": 7,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 7,
          "completed": 8170439
        }
      },
      "fs": {
        "timestamp": 1542866602104,
        "total": {
          "total_in_bytes": 1055815524352,
          "free_in_bytes": 315683545088,
          "available_in_bytes": 261979676672
        },
        "data": [
          {
            "path": "/usr/share/elasticsearch/data/nodes/0",
            "mount": "/usr/share/elasticsearch/data (/dev/sdb)",
            "type": "ext4",
            "total_in_bytes": 1055815524352,
            "free_in_bytes": 315683545088,
            "available_in_bytes": 261979676672
          }
        ],
        "io_stats": {
          "devices": [
            {
              "device_name": "sdb",
              "operations": 182498779,
              "read_operations": 110134318,
              "write_operations": 72364461,
              "read_kilobytes": 2089351396,
              "write_kilobytes": 8622515468
            }
          ],
          "total": {
            "operations": 182498779,
            "read_operations": 110134318,
            "write_operations": 72364461,
            "read_kilobytes": 2089351396,
            "write_kilobytes": 8622515468
          }
        }
      },
      "transport": {
        "server_open": 39,
        "rx_count": 12473209,
        "rx_size_in_bytes": 2092632473878,
        "tx_count": 12473208,
        "tx_size_in_bytes": 1347766194853
      },
      "http": {
        "current_open": 18,
        "total_opened": 343
      },
      "breakers": {
        "request": {
          "limit_size_in_bytes": 7694332723,
          "limit_size": "7.1gb",
          "estimated_size_in_bytes": 0,
          "estimated_size": "0b",
          "overhead": 1,
          "tripped": 0
        },
        "fielddata": {
          "limit_size_in_bytes": 10259110297,
          "limit_size": "9.5gb",
          "estimated_size_in_bytes": 920,
          "estimated_size": "920b",
          "overhead": 1.03,
          "tripped": 8
        },
        "in_flight_requests": {
          "limit_size_in_bytes": 12823887872,
          "limit_size": "11.9gb",
          "estimated_size_in_bytes": 932,
          "estimated_size": "932b",
          "overhead": 1,
          "tripped": 0
        },
        "accounting": {
          "limit_size_in_bytes": 12823887872,
          "limit_size": "11.9gb",
          "estimated_size_in_bytes": 1653546141,
          "estimated_size": "1.5gb",
          "overhead": 1,
          "tripped": 0
        },
        "parent": {
          "limit_size_in_bytes": 8976721510,
          "limit_size": "8.3gb",
          "estimated_size_in_bytes": 1653547993,
          "estimated_size": "1.5gb",
          "overhead": 1,
          "tripped": 0
        }
      },
      "script": {
        "compilations": 12,
        "cache_evictions": 0
      },
      "discovery": {
        "cluster_state_queue": {
          "total": 0,
          "pending": 0,
          "committed": 0
        },
        "published_cluster_states": {
          "full_states": 1,
          "incompatible_diffs": 0,
          "compatible_diffs": 145
        }
      },
      "ingest": {
        "total": {
          "count": 0,
          "time_in_millis": 0,
          "current": 0,
          "failed": 0
        },
        "pipelines": {
          "xpack_monitoring_2": {
            "count": 0,
            "time_in_millis": 0,
            "current": 0,
            "failed": 0,
            "processors": [
              {
                "script": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "rename": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "set": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "gsub": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              }
            ]
          },
          "xpack_monitoring_6": {
            "count": 0,
            "time_in_millis": 0,
            "current": 0,
            "failed": 0,
            "processors": [

            ]
          }
        }
      },
      "adaptive_selection": {
        "AKGUBPhiRBeSdwhI_zecGQ": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 125415,
          "avg_response_time_ns": 1254567,
          "rank": "1.3"
        },
        "KmbJ-gnWTCO7I5oemlQIgw": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 249722,
          "avg_response_time_ns": 302983,
          "rank": "0.3"
        },
        "wfm-CgU_TI6clKOgKqJG-Q": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 353344002,
          "avg_response_time_ns": 170450581,
          "rank": "170.5"
        },
        "aQxX2aAOSYuU0mZFT6JsbA": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 1026275,
          "avg_response_time_ns": 4436628,
          "rank": "4.4"
        }
      }
    },
    "wfm-CgU_TI6clKOgKqJG-Q": {
      "timestamp": 1542866602044,
      "name": "elasticsearch-1",
      "transport_address": "10.56.11.6:9300",
      "host": "10.56.11.6",
      "ip": "10.56.11.6:9300",
      "roles": [
        "master",
        "data",
        "ingest"
      ],
      "attributes": {
        "ml.machine_memory": "26843545600",
        "xpack.installed": "true",
        "ml.max_open_jobs": "20",
        "ml.enabled": "true"
      },
      "indices": {
        "docs": {
          "count": 1518736964,
          "deleted": 2050
        },
        "store": {
          "size_in_bytes": 735885045296
        },
        "indexing": {
          "index_total": 1858187084,
          "index_time_in_millis": 368082181,
          "index_current": 0,
          "index_failed": 0,
          "delete_total": 0,
          "delete_time_in_millis": 0,
          "delete_current": 0,
          "noop_update_total": 0,
          "is_throttled": false,
          "throttle_time_in_millis": 0
        },
        "get": {
          "total": 0,
          "time_in_millis": 0,
          "exists_total": 0,
          "exists_time_in_millis": 0,
          "missing_total": 0,
          "missing_time_in_millis": 0,
          "current": 0
        },
        "search": {
          "open_contexts": 0,
          "query_total": 77611,
          "query_time_in_millis": 8693637,
          "query_current": 0,
          "fetch_total": 4436,
          "fetch_time_in_millis": 14376,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 3,
          "current_docs": 6829377,
          "current_size_in_bytes": 2863805954,
          "total": 57668,
          "total_time_in_millis": 971701300,
          "total_docs": 5709531451,
          "total_size_in_bytes": 3317119701797,
          "total_stopped_time_in_millis": 112552,
          "total_throttled_time_in_millis": 749002672,
          "total_auto_throttle_in_bytes": 685457344
        },
        "refresh": {
          "total": 328904,
          "total_time_in_millis": 75037784,
          "listeners": 0
        },
        "flush": {
          "total": 4474,
          "periodic": 4438,
          "total_time_in_millis": 4789537
        },
        "warmer": {
          "current": 0,
          "total": 293710,
          "total_time_in_millis": 83873
        },
        "query_cache": {
          "memory_size_in_bytes": 107897176,
          "total_count": 206625,
          "hit_count": 101339,
          "miss_count": 105286,
          "cache_size": 279,
          "cache_count": 1382,
          "evictions": 1103
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 790,
          "memory_in_bytes": 1660893583,
          "terms_memory_in_bytes": 1329396353,
          "stored_fields_memory_in_bytes": 290675264,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 256,
          "points_memory_in_bytes": 34421038,
          "doc_values_memory_in_bytes": 6400672,
          "index_writer_memory_in_bytes": 46863984,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 10552,
          "max_unsafe_auto_id_timestamp": 1542858849367,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 7062558,
          "size_in_bytes": 7560864913,
          "uncommitted_operations": 3147887,
          "uncommitted_size_in_bytes": 3002508347,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 5758,
          "miss_count": 3189
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 811
        }
      },
      "os": {
        "timestamp": 1542866602125,
        "cpu": {
          "percent": 33,
          "load_average": {
            "1m": 4.08,
            "5m": 3.23,
            "15m": 2.8
          }
        },
        "mem": {
          "total_in_bytes": 31629697024,
          "free_in_bytes": 731938816,
          "used_in_bytes": 30897758208,
          "free_percent": 2,
          "used_percent": 98
        },
        "swap": {
          "total_in_bytes": 0,
          "free_in_bytes": 0,
          "used_in_bytes": 0
        },
        "cgroup": {
          "cpuacct": {
            "control_group": "/",
            "usage_nanos": 710321362297171
          },
          "cpu": {
            "control_group": "/",
            "cfs_period_micros": 100000,
            "cfs_quota_micros": -1,
            "stat": {
              "number_of_elapsed_periods": 0,
              "number_of_times_throttled": 0,
              "time_throttled_nanos": 0
            }
          },
          "memory": {
            "control_group": "/",
            "limit_in_bytes": "26843545600",
            "usage_in_bytes": "26841780224"
          }
        }
      },
      "process": {
        "timestamp": 1542866602125,
        "open_file_descriptors": 624,
        "max_file_descriptors": 1048576,
        "cpu": {
          "percent": 32,
          "total_in_millis": 710293850
        },
        "mem": {
          "total_virtual_in_bytes": 749538332672
        }
      },
      "jvm": {
        "timestamp": 1542866602126,
        "uptime_in_millis": 233803608,
        "mem": {
          "heap_used_in_bytes": 8912082536,
          "heap_used_percent": 69,
          "heap_committed_in_bytes": 12823887872,
          "heap_max_in_bytes": 12823887872,
          "non_heap_used_in_bytes": 156202728,
          "non_heap_committed_in_bytes": 189751296,
          "pools": {
            "young": {
              "used_in_bytes": 289127472,
              "max_in_bytes": 488636416,
              "peak_used_in_bytes": 488636416,
              "peak_max_in_bytes": 488636416
            },
            "survivor": {
              "used_in_bytes": 46738216,
              "max_in_bytes": 61014016,
              "peak_used_in_bytes": 61014016,
              "peak_max_in_bytes": 61014016
            },
            "old": {
              "used_in_bytes": 8576466544,
              "max_in_bytes": 12274237440,
              "peak_used_in_bytes": 9691590000,
              "peak_max_in_bytes": 12274237440
            }
          }
        },
        "threads": {
          "count": 104,
          "peak_count": 126
        },
        "gc": {
          "collectors": {
            "young": {
              "collection_count": 311157,
              "collection_time_in_millis": 10348324
            },
            "old": {
              "collection_count": 19989,
              "collection_time_in_millis": 1022974
            }
          }
        },
        "buffer_pools": {
          "mapped": {
            "count": 1909,
            "used_in_bytes": 730090204327,
            "total_capacity_in_bytes": 730090204327
          },
          "direct": {
            "count": 91,
            "used_in_bytes": 237985021,
            "total_capacity_in_bytes": 237985020
          }
        },
        "classes": {
          "current_loaded_count": 17529,
          "total_loaded_count": 17752,
          "total_unloaded_count": 223
        }
      },
      "thread_pool": {
        "analyze": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ccr": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "fetch_shard_started": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 14,
          "completed": 38
        },
        "fetch_shard_store": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 8,
          "completed": 39
        },
        "flush": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 35378
        },
        "force_merge": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 1,
          "completed": 4
        },
        "generic": {
          "threads": 6,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 6,
          "completed": 907880
        },
        "get": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "index": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "listener": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "management": {
          "threads": 5,
          "queue": 0,
          "active": 1,
          "rejected": 0,
          "largest": 5,
          "completed": 847353
        },
        "ml_autodetect": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ml_datafeed": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ml_utility": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "refresh": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 2408384
        },
        "rollup_indexing": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "search": {
          "threads": 11,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 11,
          "completed": 125279
        },
        "search_throttled": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "security-token-key": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "snapshot": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "warmer": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 507524
        },
        "watcher": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "write": {
          "threads": 7,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 7,
          "completed": 8161534
        }
      },
      "fs": {
        "timestamp": 1542866602127,
        "total": {
          "total_in_bytes": 1055815524352,
          "free_in_bytes": 312157917184,
          "available_in_bytes": 258454048768
        },
        "data": [
          {
            "path": "/usr/share/elasticsearch/data/nodes/0",
            "mount": "/usr/share/elasticsearch/data (/dev/sdb)",
            "type": "ext4",
            "total_in_bytes": 1055815524352,
            "free_in_bytes": 312157917184,
            "available_in_bytes": 258454048768
          }
        ],
        "io_stats": {
          "devices": [
            {
              "device_name": "sdb",
              "operations": 178662922,
              "read_operations": 106671740,
              "write_operations": 71991182,
              "read_kilobytes": 2037640700,
              "write_kilobytes": 8524116956
            }
          ],
          "total": {
            "operations": 178662922,
            "read_operations": 106671740,
            "write_operations": 71991182,
            "read_kilobytes": 2037640700,
            "write_kilobytes": 8524116956
          }
        }
      },
      "transport": {
        "server_open": 39,
        "rx_count": 15056538,
        "rx_size_in_bytes": 1788566290181,
        "tx_count": 15056539,
        "tx_size_in_bytes": 2478212531927
      },
      "http": {
        "current_open": 29,
        "total_opened": 1205
      },
      "breakers": {
        "request": {
          "limit_size_in_bytes": 7694332723,
          "limit_size": "7.1gb",
          "estimated_size_in_bytes": 0,
          "estimated_size": "0b",
          "overhead": 1,
          "tripped": 0
        },
        "fielddata": {
          "limit_size_in_bytes": 10259110297,
          "limit_size": "9.5gb",
          "estimated_size_in_bytes": 0,
          "estimated_size": "0b",
          "overhead": 1.03,
          "tripped": 8
        },
        "in_flight_requests": {
          "limit_size_in_bytes": 12823887872,
          "limit_size": "11.9gb",
          "estimated_size_in_bytes": 2,
          "estimated_size": "2b",
          "overhead": 1,
          "tripped": 0
        },
        "accounting": {
          "limit_size_in_bytes": 12823887872,
          "limit_size": "11.9gb",
          "estimated_size_in_bytes": 1660893583,
          "estimated_size": "1.5gb",
          "overhead": 1,
          "tripped": 0
        },
        "parent": {
          "limit_size_in_bytes": 8976721510,
          "limit_size": "8.3gb",
          "estimated_size_in_bytes": 1660893585,
          "estimated_size": "1.5gb",
          "overhead": 1,
          "tripped": 0
        }
      },
      "script": {
        "compilations": 12,
        "cache_evictions": 0
      },
      "discovery": {
        "cluster_state_queue": {
          "total": 0,
          "pending": 0,
          "committed": 0
        },
        "published_cluster_states": {
          "full_states": 1,
          "incompatible_diffs": 0,
          "compatible_diffs": 155
        }
      },
      "ingest": {
        "total": {
          "count": 0,
          "time_in_millis": 0,
          "current": 0,
          "failed": 0
        },
        "pipelines": {
          "xpack_monitoring_2": {
            "count": 0,
            "time_in_millis": 0,
            "current": 0,
            "failed": 0,
            "processors": [
              {
                "script": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "rename": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "set": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "gsub": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              }
            ]
          },
          "xpack_monitoring_6": {
            "count": 0,
            "time_in_millis": 0,
            "current": 0,
            "failed": 0,
            "processors": [

            ]
          }
        }
      },
      "adaptive_selection": {
        "AKGUBPhiRBeSdwhI_zecGQ": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 152712,
          "avg_response_time_ns": 1439506,
          "rank": "1.4"
        },
        "KmbJ-gnWTCO7I5oemlQIgw": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 181809,
          "avg_response_time_ns": 1059873,
          "rank": "1.1"
        },
        "wfm-CgU_TI6clKOgKqJG-Q": {
          "outgoing_searches": 0,
          "avg_queue_size": 1,
          "avg_service_time_ns": 13922164,
          "avg_response_time_ns": 184973595,
          "rank": "185.5"
        },
        "aQxX2aAOSYuU0mZFT6JsbA": {
          "outgoing_searches": 0,
          "avg_queue_size": 1,
          "avg_service_time_ns": 220855742,
          "avg_response_time_ns": 2131669821,
          "rank": "2131.7"
        }
      }
    },
    "AKGUBPhiRBeSdwhI_zecGQ": {
      "timestamp": 1542866602045,
      "name": "elasticsearch-3",
      "transport_address": "10.56.10.5:9300",
      "host": "10.56.10.5",
      "ip": "10.56.10.5:9300",
      "roles": [
        "master",
        "data",
        "ingest"
      ],
      "attributes": {
        "ml.machine_memory": "26843545600",
        "ml.max_open_jobs": "20",
        "xpack.installed": "true",
        "ml.enabled": "true"
      },
      "indices": {
        "docs": {
          "count": 1513167321,
          "deleted": 1534
        },
        "store": {
          "size_in_bytes": 731491242302
        },
        "indexing": {
          "index_total": 1852551260,
          "index_time_in_millis": 365379567,
          "index_current": 0,
          "index_failed": 0,
          "delete_total": 0,
          "delete_time_in_millis": 0,
          "delete_current": 0,
          "noop_update_total": 0,
          "is_throttled": false,
          "throttle_time_in_millis": 0
        },
        "get": {
          "total": 23375,
          "time_in_millis": 1843,
          "exists_total": 11856,
          "exists_time_in_millis": 1037,
          "missing_total": 11519,
          "missing_time_in_millis": 806,
          "current": 0
        },
        "search": {
          "open_contexts": 0,
          "query_total": 153107,
          "query_time_in_millis": 8477407,
          "query_current": 0,
          "fetch_total": 83053,
          "fetch_time_in_millis": 13146,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 2,
          "current_docs": 1121577,
          "current_size_in_bytes": 437021015,
          "total": 58563,
          "total_time_in_millis": 962772395,
          "total_docs": 5708371191,
          "total_size_in_bytes": 3318186569738,
          "total_stopped_time_in_millis": 80550,
          "total_throttled_time_in_millis": 735576101,
          "total_auto_throttle_in_bytes": 674826746
        },
        "refresh": {
          "total": 326489,
          "total_time_in_millis": 68423480,
          "listeners": 0
        },
        "flush": {
          "total": 4463,
          "periodic": 4419,
          "total_time_in_millis": 4183799
        },
        "warmer": {
          "current": 0,
          "total": 280363,
          "total_time_in_millis": 70452
        },
        "query_cache": {
          "memory_size_in_bytes": 97491400,
          "total_count": 153876,
          "hit_count": 72848,
          "miss_count": 81028,
          "cache_size": 238,
          "cache_count": 1570,
          "evictions": 1332
        },
        "fielddata": {
          "memory_size_in_bytes": 920,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 760,
          "memory_in_bytes": 1697946292,
          "terms_memory_in_bytes": 1366598433,
          "stored_fields_memory_in_bytes": 290521520,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 1408,
          "points_memory_in_bytes": 34281907,
          "doc_values_memory_in_bytes": 6543024,
          "index_writer_memory_in_bytes": 54754376,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542844801872,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 5596859,
          "size_in_bytes": 6077329232,
          "uncommitted_operations": 2330533,
          "uncommitted_size_in_bytes": 1833451545,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 848,
          "evictions": 0,
          "hit_count": 20038,
          "miss_count": 3917
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 644
        }
      },
      "os": {
        "timestamp": 1542866602120,
        "cpu": {
          "percent": 25,
          "load_average": {
            "1m": 2.69,
            "5m": 2.55,
            "15m": 2.48
          }
        },
        "mem": {
          "total_in_bytes": 31629697024,
          "free_in_bytes": 1133215744,
          "used_in_bytes": 30496481280,
          "free_percent": 4,
          "used_percent": 96
        },
        "swap": {
          "total_in_bytes": 0,
          "free_in_bytes": 0,
          "used_in_bytes": 0
        },
        "cgroup": {
          "cpuacct": {
            "control_group": "/",
            "usage_nanos": 690158229676277
          },
          "cpu": {
            "control_group": "/",
            "cfs_period_micros": 100000,
            "cfs_quota_micros": -1,
            "stat": {
              "number_of_elapsed_periods": 0,
              "number_of_times_throttled": 0,
              "time_throttled_nanos": 0
            }
          },
          "memory": {
            "control_group": "/",
            "limit_in_bytes": "26843545600",
            "usage_in_bytes": "26356461568"
          }
        }
      },
      "process": {
        "timestamp": 1542866602120,
        "open_file_descriptors": 579,
        "max_file_descriptors": 1048576,
        "cpu": {
          "percent": 25,
          "total_in_millis": 690130600
        },
        "mem": {
          "total_virtual_in_bytes": 748658315264
        }
      },
      "jvm": {
        "timestamp": 1542866602121,
        "uptime_in_millis": 233767722,
        "mem": {
          "heap_used_in_bytes": 3384301576,
          "heap_used_percent": 26,
          "heap_committed_in_bytes": 12823887872,
          "heap_max_in_bytes": 12823887872,
          "non_heap_used_in_bytes": 154169936,
          "non_heap_committed_in_bytes": 186396672,
          "pools": {
            "young": {
              "used_in_bytes": 352999880,
              "max_in_bytes": 488636416,
              "peak_used_in_bytes": 488636416,
              "peak_max_in_bytes": 488636416
            },
            "survivor": {
              "used_in_bytes": 42020288,
              "max_in_bytes": 61014016,
              "peak_used_in_bytes": 61014016,
              "peak_max_in_bytes": 61014016
            },
            "old": {
              "used_in_bytes": 2989356696,
              "max_in_bytes": 12274237440,
              "peak_used_in_bytes": 9713371888,
              "peak_max_in_bytes": 12274237440
            }
          }
        },
        "threads": {
          "count": 107,
          "peak_count": 122
        },
        "gc": {
          "collectors": {
            "young": {
              "collection_count": 301251,
              "collection_time_in_millis": 9430616
            },
            "old": {
              "collection_count": 20580,
              "collection_time_in_millis": 990347
            }
          }
        },
        "buffer_pools": {
          "mapped": {
            "count": 1897,
            "used_in_bytes": 729217076719,
            "total_capacity_in_bytes": 729217076719
          },
          "direct": {
            "count": 90,
            "used_in_bytes": 237975584,
            "total_capacity_in_bytes": 237975583
          }
        },
        "classes": {
          "current_loaded_count": 17476,
          "total_loaded_count": 17708,
          "total_unloaded_count": 232
        }
      },
      "thread_pool": {
        "analyze": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ccr": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "fetch_shard_started": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 9,
          "completed": 9
        },
        "fetch_shard_store": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 1,
          "completed": 17
        },
        "flush": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 35277
        },
        "force_merge": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 1,
          "completed": 3
        },
        "generic": {
          "threads": 6,
          "queue": 0,
          "active": 1,
          "rejected": 0,
          "largest": 6,
          "completed": 921506
        },
        "get": {
          "threads": 7,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 7,
          "completed": 23375
        },
        "index": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "listener": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "management": {
          "threads": 5,
          "queue": 0,
          "active": 2,
          "rejected": 0,
          "largest": 5,
          "completed": 878338
        },
        "ml_autodetect": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ml_datafeed": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ml_utility": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "refresh": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 2348837
        },
        "rollup_indexing": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "search": {
          "threads": 11,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 11,
          "completed": 240399
        },
        "search_throttled": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "security-token-key": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "snapshot": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "warmer": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 414240
        },
        "watcher": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "write": {
          "threads": 7,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 7,
          "completed": 8149924
        }
      },
      "fs": {
        "timestamp": 1542866602122,
        "total": {
          "total_in_bytes": 1055815524352,
          "free_in_bytes": 318502023168,
          "available_in_bytes": 264798154752
        },
        "data": [
          {
            "path": "/usr/share/elasticsearch/data/nodes/0",
            "mount": "/usr/share/elasticsearch/data (/dev/sdb)",
            "type": "ext4",
            "total_in_bytes": 1055815524352,
            "free_in_bytes": 318502023168,
            "available_in_bytes": 264798154752
          }
        ],
        "io_stats": {
          "devices": [
            {
              "device_name": "sdb",
              "operations": 183107111,
              "read_operations": 111185281,
              "write_operations": 71921830,
              "read_kilobytes": 2029756092,
              "write_kilobytes": 8514840888
            }
          ],
          "total": {
            "operations": 183107111,
            "read_operations": 111185281,
            "write_operations": 71921830,
            "read_kilobytes": 2029756092,
            "write_kilobytes": 8514840888
          }
        }
      },
      "transport": {
        "server_open": 39,
        "rx_count": 13376523,
        "rx_size_in_bytes": 2030779112225,
        "tx_count": 13376522,
        "tx_size_in_bytes": 1589950367089
      },
      "http": {
        "current_open": 14,
        "total_opened": 449
      },
      "breakers": {
        "request": {
          "limit_size_in_bytes": 7694332723,
          "limit_size": "7.1gb",
          "estimated_size_in_bytes": 0,
          "estimated_size": "0b",
          "overhead": 1,
          "tripped": 0
        },
        "fielddata": {
          "limit_size_in_bytes": 10259110297,
          "limit_size": "9.5gb",
          "estimated_size_in_bytes": 920,
          "estimated_size": "920b",
          "overhead": 1.03,
          "tripped": 8
        },
        "in_flight_requests": {
          "limit_size_in_bytes": 12823887872,
          "limit_size": "11.9gb",
          "estimated_size_in_bytes": 932,
          "estimated_size": "932b",
          "overhead": 1,
          "tripped": 0
        },
        "accounting": {
          "limit_size_in_bytes": 12823887872,
          "limit_size": "11.9gb",
          "estimated_size_in_bytes": 1697946292,
          "estimated_size": "1.5gb",
          "overhead": 1,
          "tripped": 0
        },
        "parent": {
          "limit_size_in_bytes": 8976721510,
          "limit_size": "8.3gb",
          "estimated_size_in_bytes": 1697948144,
          "estimated_size": "1.5gb",
          "overhead": 1,
          "tripped": 71863
        }
      },
      "script": {
        "compilations": 12,
        "cache_evictions": 0
      },
      "discovery": {
        "cluster_state_queue": {
          "total": 0,
          "pending": 0,
          "committed": 0
        },
        "published_cluster_states": {
          "full_states": 1,
          "incompatible_diffs": 0,
          "compatible_diffs": 127
        }
      },
      "ingest": {
        "total": {
          "count": 0,
          "time_in_millis": 0,
          "current": 0,
          "failed": 0
        },
        "pipelines": {
          "xpack_monitoring_2": {
            "count": 0,
            "time_in_millis": 0,
            "current": 0,
            "failed": 0,
            "processors": [
              {
                "script": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "rename": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "set": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "gsub": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              }
            ]
          },
          "xpack_monitoring_6": {
            "count": 0,
            "time_in_millis": 0,
            "current": 0,
            "failed": 0,
            "processors": [

            ]
          }
        }
      },
      "adaptive_selection": {
        "AKGUBPhiRBeSdwhI_zecGQ": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 184787,
          "avg_response_time_ns": 317616,
          "rank": "0.3"
        },
        "KmbJ-gnWTCO7I5oemlQIgw": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 229042,
          "avg_response_time_ns": 1046785,
          "rank": "1.0"
        },
        "wfm-CgU_TI6clKOgKqJG-Q": {
          "outgoing_searches": 0,
          "avg_queue_size": 3,
          "avg_service_time_ns": 2081800,
          "avg_response_time_ns": 8958905,
          "rank": "39.2"
        },
        "aQxX2aAOSYuU0mZFT6JsbA": {
          "outgoing_searches": 0,
          "avg_queue_size": 3,
          "avg_service_time_ns": 2764148,
          "avg_response_time_ns": 6927282,
          "rank": "29.7"
        }
      }
    },
    "aQxX2aAOSYuU0mZFT6JsbA": {
      "timestamp": 1542866602045,
      "name": "elasticsearch-0",
      "transport_address": "10.56.8.5:9300",
      "host": "10.56.8.5",
      "ip": "10.56.8.5:9300",
      "roles": [
        "master",
        "data",
        "ingest"
      ],
      "attributes": {
        "ml.machine_memory": "26843545600",
        "ml.max_open_jobs": "20",
        "xpack.installed": "true",
        "ml.enabled": "true"
      },
      "indices": {
        "docs": {
          "count": 1518155357,
          "deleted": 3986
        },
        "store": {
          "size_in_bytes": 734603578283
        },
        "indexing": {
          "index_total": 1858708569,
          "index_time_in_millis": 370923237,
          "index_current": 0,
          "index_failed": 0,
          "delete_total": 0,
          "delete_time_in_millis": 0,
          "delete_current": 0,
          "noop_update_total": 0,
          "is_throttled": false,
          "throttle_time_in_millis": 0
        },
        "get": {
          "total": 43,
          "time_in_millis": 57,
          "exists_total": 22,
          "exists_time_in_millis": 41,
          "missing_total": 21,
          "missing_time_in_millis": 16,
          "current": 0
        },
        "search": {
          "open_contexts": 0,
          "query_total": 88133,
          "query_time_in_millis": 9681029,
          "query_current": 0,
          "fetch_total": 7007,
          "fetch_time_in_millis": 13465,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 3,
          "current_docs": 7166759,
          "current_size_in_bytes": 3125368616,
          "total": 65816,
          "total_time_in_millis": 967115375,
          "total_docs": 5735868455,
          "total_size_in_bytes": 3341189979165,
          "total_stopped_time_in_millis": 108472,
          "total_throttled_time_in_millis": 737393882,
          "total_auto_throttle_in_bytes": 862611744
        },
        "refresh": {
          "total": 405537,
          "total_time_in_millis": 69395352,
          "listeners": 0
        },
        "flush": {
          "total": 4474,
          "periodic": 4439,
          "total_time_in_millis": 4158812
        },
        "warmer": {
          "current": 0,
          "total": 341975,
          "total_time_in_millis": 98420
        },
        "query_cache": {
          "memory_size_in_bytes": 108241680,
          "total_count": 285941,
          "hit_count": 100992,
          "miss_count": 184949,
          "cache_size": 263,
          "cache_count": 2255,
          "evictions": 1992
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 775,
          "memory_in_bytes": 1701089439,
          "terms_memory_in_bytes": 1370477730,
          "stored_fields_memory_in_bytes": 291070488,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 64,
          "points_memory_in_bytes": 34454337,
          "doc_values_memory_in_bytes": 5086820,
          "index_writer_memory_in_bytes": 26077160,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 10480,
          "max_unsafe_auto_id_timestamp": 1542862101307,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 6904939,
          "size_in_bytes": 7253830266,
          "uncommitted_operations": 1974535,
          "uncommitted_size_in_bytes": 1759977496,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 18956,
          "miss_count": 6653
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 215
        }
      },
      "os": {
        "timestamp": 1542866602177,
        "cpu": {
          "percent": 39,
          "load_average": {
            "1m": 2.17,
            "5m": 2.12,
            "15m": 2.23
          }
        },
        "mem": {
          "total_in_bytes": 31629697024,
          "free_in_bytes": 421085184,
          "used_in_bytes": 31208611840,
          "free_percent": 1,
          "used_percent": 99
        },
        "swap": {
          "total_in_bytes": 0,
          "free_in_bytes": 0,
          "used_in_bytes": 0
        },
        "cgroup": {
          "cpuacct": {
            "control_group": "/",
            "usage_nanos": 717422284099272
          },
          "cpu": {
            "control_group": "/",
            "cfs_period_micros": 100000,
            "cfs_quota_micros": -1,
            "stat": {
              "number_of_elapsed_periods": 0,
              "number_of_times_throttled": 0,
              "time_throttled_nanos": 0
            }
          },
          "memory": {
            "control_group": "/",
            "limit_in_bytes": "26843545600",
            "usage_in_bytes": "26839478272"
          }
        }
      },
      "process": {
        "timestamp": 1542866602177,
        "open_file_descriptors": 603,
        "max_file_descriptors": 1048576,
        "cpu": {
          "percent": 39,
          "total_in_millis": 717391110
        },
        "mem": {
          "total_virtual_in_bytes": 750940815360
        }
      },
      "jvm": {
        "timestamp": 1542866602178,
        "uptime_in_millis": 233846893,
        "mem": {
          "heap_used_in_bytes": 5914556928,
          "heap_used_percent": 46,
          "heap_committed_in_bytes": 12823887872,
          "heap_max_in_bytes": 12823887872,
          "non_heap_used_in_bytes": 163251696,
          "non_heap_committed_in_bytes": 199831552,
          "pools": {
            "young": {
              "used_in_bytes": 250893768,
              "max_in_bytes": 488636416,
              "peak_used_in_bytes": 488636416,
              "peak_max_in_bytes": 488636416
            },
            "survivor": {
              "used_in_bytes": 32297496,
              "max_in_bytes": 61014016,
              "peak_used_in_bytes": 61014016,
              "peak_max_in_bytes": 61014016
            },
            "old": {
              "used_in_bytes": 5631365664,
              "max_in_bytes": 12274237440,
              "peak_used_in_bytes": 9864844200,
              "peak_max_in_bytes": 12274237440
            }
          }
        },
        "threads": {
          "count": 128,
          "peak_count": 137
        },
        "gc": {
          "collectors": {
            "young": {
              "collection_count": 308186,
              "collection_time_in_millis": 9753684
            },
            "old": {
              "collection_count": 28397,
              "collection_time_in_millis": 1466279
            }
          }
        },
        "buffer_pools": {
          "mapped": {
            "count": 1894,
            "used_in_bytes": 731480442234,
            "total_capacity_in_bytes": 731480442234
          },
          "direct": {
            "count": 90,
            "used_in_bytes": 237971996,
            "total_capacity_in_bytes": 237971995
          }
        },
        "classes": {
          "current_loaded_count": 18018,
          "total_loaded_count": 18259,
          "total_unloaded_count": 241
        }
      },
      "thread_pool": {
        "analyze": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ccr": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "fetch_shard_started": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 14,
          "completed": 57
        },
        "fetch_shard_store": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 10,
          "completed": 39
        },
        "flush": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 35375
        },
        "force_merge": {
          "threads": 1,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 1,
          "completed": 4
        },
        "generic": {
          "threads": 5,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 5,
          "completed": 711053
        },
        "get": {
          "threads": 7,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 7,
          "completed": 43
        },
        "index": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "listener": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "management": {
          "threads": 5,
          "queue": 0,
          "active": 1,
          "rejected": 0,
          "largest": 5,
          "completed": 894426
        },
        "ml_autodetect": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ml_datafeed": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "ml_utility": {
          "threads": 18,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 18,
          "completed": 18
        },
        "refresh": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 2722977
        },
        "rollup_indexing": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "search": {
          "threads": 11,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 11,
          "completed": 134811
        },
        "search_throttled": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "security-token-key": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "snapshot": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "warmer": {
          "threads": 4,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 4,
          "completed": 1120122
        },
        "watcher": {
          "threads": 0,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 0,
          "completed": 0
        },
        "write": {
          "threads": 7,
          "queue": 0,
          "active": 0,
          "rejected": 0,
          "largest": 7,
          "completed": 8142163
        }
      },
      "fs": {
        "timestamp": 1542866602178,
        "total": {
          "total_in_bytes": 1055815524352,
          "free_in_bytes": 313719480320,
          "available_in_bytes": 260015611904
        },
        "least_usage_estimate": {
          "path": "/usr/share/elasticsearch/data/nodes/0",
          "total_in_bytes": 1055815524352,
          "available_in_bytes": 260194033664,
          "used_disk_percent": 75.35610836716079
        },
        "most_usage_estimate": {
          "path": "/usr/share/elasticsearch/data/nodes/0",
          "total_in_bytes": 1055815524352,
          "available_in_bytes": 260194033664,
          "used_disk_percent": 75.35610836716079
        },
        "data": [
          {
            "path": "/usr/share/elasticsearch/data/nodes/0",
            "mount": "/usr/share/elasticsearch/data (/dev/sdb)",
            "type": "ext4",
            "total_in_bytes": 1055815524352,
            "free_in_bytes": 313719480320,
            "available_in_bytes": 260015611904
          }
        ],
        "io_stats": {
          "devices": [
            {
              "device_name": "sdb",
              "operations": 184217055,
              "read_operations": 111848695,
              "write_operations": 72368360,
              "read_kilobytes": 2009276600,
              "write_kilobytes": 8595482792
            }
          ],
          "total": {
            "operations": 184217055,
            "read_operations": 111848695,
            "write_operations": 72368360,
            "read_kilobytes": 2009276600,
            "write_kilobytes": 8595482792
          }
        }
      },
      "transport": {
        "server_open": 39,
        "rx_count": 16193696,
        "rx_size_in_bytes": 1834678279278,
        "tx_count": 16193695,
        "tx_size_in_bytes": 2330727002555
      },
      "http": {
        "current_open": 15,
        "total_opened": 382
      },
      "breakers": {
        "request": {
          "limit_size_in_bytes": 7694332723,
          "limit_size": "7.1gb",
          "estimated_size_in_bytes": 0,
          "estimated_size": "0b",
          "overhead": 1,
          "tripped": 0
        },
        "fielddata": {
          "limit_size_in_bytes": 10259110297,
          "limit_size": "9.5gb",
          "estimated_size_in_bytes": 0,
          "estimated_size": "0b",
          "overhead": 1.03,
          "tripped": 8
        },
        "in_flight_requests": {
          "limit_size_in_bytes": 12823887872,
          "limit_size": "11.9gb",
          "estimated_size_in_bytes": 932,
          "estimated_size": "932b",
          "overhead": 1,
          "tripped": 0
        },
        "accounting": {
          "limit_size_in_bytes": 12823887872,
          "limit_size": "11.9gb",
          "estimated_size_in_bytes": 1701089439,
          "estimated_size": "1.5gb",
          "overhead": 1,
          "tripped": 0
        },
        "parent": {
          "limit_size_in_bytes": 8976721510,
          "limit_size": "8.3gb",
          "estimated_size_in_bytes": 1701090371,
          "estimated_size": "1.5gb",
          "overhead": 1,
          "tripped": 1166
        }
      },
      "script": {
        "compilations": 11,
        "cache_evictions": 0
      },
      "discovery": {
        "cluster_state_queue": {
          "total": 0,
          "pending": 0,
          "committed": 0
        },
        "published_cluster_states": {
          "full_states": 0,
          "incompatible_diffs": 0,
          "compatible_diffs": 0
        }
      },
      "ingest": {
        "total": {
          "count": 0,
          "time_in_millis": 0,
          "current": 0,
          "failed": 0
        },
        "pipelines": {
          "xpack_monitoring_2": {
            "count": 0,
            "time_in_millis": 0,
            "current": 0,
            "failed": 0,
            "processors": [
              {
                "script": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "rename": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "set": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              },
              {
                "gsub": {
                  "count": 0,
                  "time_in_millis": 0,
                  "current": 0,
                  "failed": 0
                }
              }
            ]
          },
          "xpack_monitoring_6": {
            "count": 0,
            "time_in_millis": 0,
            "current": 0,
            "failed": 0,
            "processors": [

            ]
          }
        }
      },
      "adaptive_selection": {
        "AKGUBPhiRBeSdwhI_zecGQ": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 159300,
          "avg_response_time_ns": 1845178,
          "rank": "1.8"
        },
        "KmbJ-gnWTCO7I5oemlQIgw": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 255397,
          "avg_response_time_ns": 1133743,
          "rank": "1.1"
        },
        "wfm-CgU_TI6clKOgKqJG-Q": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 303393743,
          "avg_response_time_ns": 351869811,
          "rank": "351.9"
        },
        "aQxX2aAOSYuU0mZFT6JsbA": {
          "outgoing_searches": 0,
          "avg_queue_size": 0,
          "avg_service_time_ns": 4144453,
          "avg_response_time_ns": 6900348,
          "rank": "6.9"
        }
      }
    }
  }
}
"""
)

def list_telemetry():
    console.println("Available telemetry devices:\n")
    devices = [[device.command, device.human_name, device.help] for device in [JitCompiler, Gc, FlightRecorder, PerfStat, NodeStats]]
    console.println(tabulate.tabulate(devices, ["Command", "Name", "Description"]))
    console.println("\nKeep in mind that each telemetry device may incur a runtime overhead which can skew results.")


class Telemetry:
    def __init__(self, enabled_devices=None, devices=None):
        if devices is None:
            devices = []
        if enabled_devices is None:
            enabled_devices = []
        self.enabled_devices = enabled_devices
        self.devices = devices

    def instrument_candidate_env(self, car, candidate_id):
        opts = {}
        for device in self.devices:
            if self._enabled(device):
                additional_opts = device.instrument_env(car, candidate_id)
                # properly merge values with the same key
                for k, v in additional_opts.items():
                    if k in opts:
                        opts[k] = "%s %s" % (opts[k], v)
                    else:
                        opts[k] = v
        return opts

    def attach_to_cluster(self, cluster):
        for device in self.devices:
            if self._enabled(device):
                device.attach_to_cluster(cluster)

    def on_pre_node_start(self, node_name):
        for device in self.devices:
            if self._enabled(device):
                device.on_pre_node_start(node_name)

    def attach_to_node(self, node):
        for device in self.devices:
            if self._enabled(device):
                device.attach_to_node(node)

    def detach_from_node(self, node, running):
        for device in self.devices:
            if self._enabled(device):
                device.detach_from_node(node, running)

    def on_benchmark_start(self):
        for device in self.devices:
            if self._enabled(device):
                device.on_benchmark_start()

    def on_benchmark_stop(self):
        for device in self.devices:
            if self._enabled(device):
                device.on_benchmark_stop()

    def detach_from_cluster(self, cluster):
        for device in self.devices:
            if self._enabled(device):
                device.detach_from_cluster(cluster)

    def _enabled(self, device):
        return device.internal or device.command in self.enabled_devices


########################################################################################
#
# Telemetry devices
#
########################################################################################

class TelemetryDevice:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def instrument_env(self, car, candidate_id):
        return {}

    def attach_to_cluster(self, cluster):
        pass

    def on_pre_node_start(self, node_name):
        pass

    def attach_to_node(self, node):
        pass

    def detach_from_node(self, node, running):
        pass

    def detach_from_cluster(self, cluster):
        pass

    def on_benchmark_start(self):
        pass

    def on_benchmark_stop(self):
        pass


class InternalTelemetryDevice(TelemetryDevice):
    internal = True


class SamplerThread(threading.Thread):
    def __init__(self, recorder):
        threading.Thread.__init__(self)
        self.stop = False
        self.recorder = recorder

    def finish(self):
        self.stop = True
        self.join()

    def run(self):
        # noinspection PyBroadException
        try:
            while not self.stop:
                self.recorder.record()
                time.sleep(self.recorder.sample_interval)
        except BaseException:
            logging.getLogger(__name__).exception("Could not determine %s", self.recorder)


class FlightRecorder(TelemetryDevice):
    internal = False
    command = "jfr"
    human_name = "Flight Recorder"
    help = "Enables Java Flight Recorder (requires an Oracle JDK or OpenJDK 11+)"

    def __init__(self, telemetry_params, log_root, java_major_version):
        super().__init__()
        self.telemetry_params = telemetry_params
        self.log_root = log_root
        self.java_major_version = java_major_version

    def instrument_env(self, car, candidate_id):
        io.ensure_dir(self.log_root)
        log_file = "%s/%s-%s.jfr" % (self.log_root, car.safe_name, candidate_id)

        # JFR was integrated into OpenJDK 11 and is not a commercial feature anymore.
        if self.java_major_version < 11:
            console.println("\n***************************************************************************\n")
            console.println("[WARNING] Java flight recorder is a commercial feature of the Oracle JDK.\n")
            console.println("You are using Java flight recorder which requires that you comply with\nthe licensing terms stated in:\n")
            console.println(console.format.link("http://www.oracle.com/technetwork/java/javase/terms/license/index.html"))
            console.println("\nBy using this feature you confirm that you comply with these license terms.\n")
            console.println("Otherwise, please abort and rerun Rally without the \"jfr\" telemetry device.")
            console.println("\n***************************************************************************\n")

            time.sleep(3)

        console.info("%s: Writing flight recording to [%s]" % (self.human_name, log_file), logger=self.logger)

        java_opts = self.java_opts(log_file)

        self.logger.info("jfr: Adding JVM arguments: [%s].", java_opts)
        return {"ES_JAVA_OPTS": java_opts}

    def java_opts(self, log_file):
        recording_template = self.telemetry_params.get("recording-template")
        java_opts = "-XX:+UnlockDiagnosticVMOptions -XX:+DebugNonSafepoints "

        if self.java_major_version < 11:
            java_opts += "-XX:+UnlockCommercialFeatures "

        if self.java_major_version < 9:
            java_opts += "-XX:+FlightRecorder "
            java_opts += "-XX:FlightRecorderOptions=disk=true,maxage=0s,maxsize=0,dumponexit=true,dumponexitpath={} ".format(log_file)
            java_opts += "-XX:StartFlightRecording=defaultrecording=true"
            if recording_template:
                self.logger.info("jfr: Using recording template [%s].", recording_template)
                java_opts += ",settings={}".format(recording_template)
            else:
                self.logger.info("jfr: Using default recording template.")
        else:
            java_opts += "-XX:StartFlightRecording=maxsize=0,maxage=0s,disk=true,dumponexit=true,filename={}".format(log_file)
            if recording_template:
                self.logger.info("jfr: Using recording template [%s].", recording_template)
                java_opts += ",settings={}".format(recording_template)
            else:
                self.logger.info("jfr: Using default recording template.")
        return java_opts


class JitCompiler(TelemetryDevice):
    internal = False
    command = "jit"
    human_name = "JIT Compiler Profiler"
    help = "Enables JIT compiler logs."

    def __init__(self, log_root):
        super().__init__()
        self.log_root = log_root

    def instrument_env(self, car, candidate_id):
        io.ensure_dir(self.log_root)
        log_file = "%s/%s-%s.jit.log" % (self.log_root, car.safe_name, candidate_id)
        console.info("%s: Writing JIT compiler log to [%s]" % (self.human_name, log_file), logger=self.logger)
        return {"ES_JAVA_OPTS": "-XX:+UnlockDiagnosticVMOptions -XX:+TraceClassLoading -XX:+LogCompilation "
                                "-XX:LogFile=%s -XX:+PrintAssembly" % log_file}


class Gc(TelemetryDevice):
    internal = False
    command = "gc"
    human_name = "GC log"
    help = "Enables GC logs."

    def __init__(self, log_root, java_major_version):
        super().__init__()
        self.log_root = log_root
        self.java_major_version = java_major_version

    def instrument_env(self, car, candidate_id):
        io.ensure_dir(self.log_root)
        log_file = "%s/%s-%s.gc.log" % (self.log_root, car.safe_name, candidate_id)
        console.info("%s: Writing GC log to [%s]" % (self.human_name, log_file), logger=self.logger)
        return self.java_opts(log_file)

    def java_opts(self, log_file):
        if self.java_major_version < 9:
            return {"ES_JAVA_OPTS": "-Xloggc:%s -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+PrintGCTimeStamps "
                                    "-XX:+PrintGCApplicationStoppedTime -XX:+PrintGCApplicationConcurrentTime "
                                    "-XX:+PrintTenuringDistribution" % log_file}
        else:
            # see https://docs.oracle.com/javase/9/tools/java.htm#JSWOR-GUID-BE93ABDC-999C-4CB5-A88B-1994AAAC74D5
            return {"ES_JAVA_OPTS": "-Xlog:gc*=info,safepoint=info,age*=trace:file=%s:utctime,uptimemillis,level,tags:filecount=0" % log_file}


class PerfStat(TelemetryDevice):
    internal = False
    command = "perf"
    human_name = "perf stat"
    help = "Reads CPU PMU counters (requires Linux and perf)"

    def __init__(self, log_root):
        super().__init__()
        self.log_root = log_root
        self.process = None
        self.node = None
        self.log = None
        self.attached = False

    def attach_to_node(self, node):
        io.ensure_dir(self.log_root)
        log_file = "%s/%s.perf.log" % (self.log_root, node.node_name)

        console.info("%s: Writing perf logs to [%s]" % (self.human_name, log_file), logger=self.logger)

        self.log = open(log_file, "wb")

        self.process = subprocess.Popen(["perf", "stat", "-p %s" % node.process.pid],
                                        stdout=self.log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        self.node = node
        self.attached = True

    def detach_from_node(self, node, running):
        if self.attached and running:
            self.logger.info("Dumping PMU counters for node [%s]", node.node_name)
            os.kill(self.process.pid, signal.SIGINT)
            try:
                self.process.wait(10.0)
            except subprocess.TimeoutExpired:
                self.logger.warning("perf stat did not terminate")
            self.log.close()
            self.attached = False


class CcrStats(TelemetryDevice):
    internal = False
    command = "ccr-stats"
    human_name = "CCR Stats"
    help = "Regularly samples Cross Cluster Replication (CCR) related stats"

    """
    Gathers CCR stats on a cluster level
    """

    def __init__(self, telemetry_params, clients, metrics_store):
        """
        :param telemetry_params: The configuration object for telemetry_params.
            May optionally specify:
            ``ccr-stats-indices``: JSON string specifying the indices per cluster to publish statistics from.
            Not all clusters need to be specified, but any name used must be be present in target.hosts.
            Example:
            {"ccr-stats-indices": {"cluster_a": ["follower"],"default": ["leader"]}
            ``ccr-stats-sample-interval``: positive integer controlling the sampling interval. Default: 1 second.
        :param clients: A dict of clients to all clusters.
        :param metrics_store: The configured metrics store we write to.
        """
        super().__init__()

        self.telemetry_params = telemetry_params
        self.clients = clients
        self.sample_interval = telemetry_params.get("ccr-stats-sample-interval", 1)
        if self.sample_interval <= 0:
            raise exceptions.SystemSetupError(
                "The telemetry parameter 'ccr-stats-sample-interval' must be greater than zero but was {}.".format(self.sample_interval))
        self.specified_cluster_names = self.clients.keys()
        self.indices_per_cluster = self.telemetry_params.get("ccr-stats-indices", False)
        if self.indices_per_cluster:
            for cluster_name in self.indices_per_cluster.keys():
                if cluster_name not in clients:
                    raise exceptions.SystemSetupError(
                        "The telemetry parameter 'ccr-stats-indices' must be a JSON Object with keys matching "
                        "the cluster names [{}] specified in --target-hosts "
                        "but it had [{}].".format(",".join(sorted(clients.keys())), cluster_name))
            self.specified_cluster_names = self.indices_per_cluster.keys()

        self.metrics_store = metrics_store
        self.samplers = []

    def attach_to_cluster(self, cluster):
        # This cluster parameter does not correspond to the cluster names passed in target.hosts, see on_benchmark_start()
        super().attach_to_cluster(cluster)

    def on_benchmark_start(self):
        recorder = []
        for cluster_name in self.specified_cluster_names:
            recorder = CcrStatsRecorder(cluster_name, self.clients[cluster_name], self.metrics_store, self.sample_interval,
                                        self.indices_per_cluster[cluster_name] if self.indices_per_cluster else None)
            sampler = SamplerThread(recorder)
            self.samplers.append(sampler)
            sampler.setDaemon(True)
            # we don't require starting recorders precisely at the same time
            sampler.start()

    def on_benchmark_stop(self):
        if self.samplers:
            for sampler in self.samplers:
                sampler.finish()


class CcrStatsRecorder:
    """
    Collects and pushes CCR stats for the specified cluster to the metric store.
    """

    def __init__(self, cluster_name, client, metrics_store, sample_interval, indices=None):
        """
        :param cluster_name: The cluster_name that the client connects to, as specified in target.hosts.
        :param client: The Elasticsearch client for this cluster.
        :param metrics_store: The configured metrics store we write to.
        :param sample_interval: integer controlling the interval, in seconds, between collecting samples.
        :param indices: optional list of indices to filter results from.
        """

        self.cluster_name = cluster_name
        self.client = client
        self.metrics_store = metrics_store
        self.sample_interval= sample_interval
        self.indices = indices
        self.logger = logging.getLogger(__name__)

    def __str__(self):
        return "ccr stats"

    def record(self):
        """
        Collect CCR stats for indexes (optionally) specified in telemetry parameters and push to metrics store.
        """

        # ES returns all stats values in bytes or ms via "human: false"

        import elasticsearch

        try:
            ccr_stats_api_endpoint = "/_ccr/stats"
            filter_path = "follow_stats"
            stats = self.client.transport.perform_request("GET", ccr_stats_api_endpoint, params={"human": "false",
                                                                                                 "filter_path": filter_path})
        except elasticsearch.TransportError as e:
            msg = "A transport error occurred while collecting CCR stats from the endpoint [{}?filter_path={}] on " \
                  "cluster [{}]".format(ccr_stats_api_endpoint, filter_path, self.cluster_name)
            self.logger.exception(msg)
            raise exceptions.RallyError(msg)

        if filter_path in stats and "indices" in stats[filter_path]:
            for indices in stats[filter_path]["indices"]:
                try:
                    if self.indices and indices["index"] not in self.indices:
                        # Skip metrics for indices not part of user supplied whitelist (ccr-stats-indices) in telemetry params.
                        continue
                    self.record_stats_per_index(indices["index"], indices["shards"])
                except KeyError:
                    self.logger.warning(
                        "The 'indices' key in {0} does not contain an 'index' or 'shards' key "
                        "Maybe the output format of the {0} endpoint has changed. Skipping.".format(ccr_stats_api_endpoint)
                    )
        time.sleep(self.sample_interval)

    def record_stats_per_index(self, name, stats):
        """
        :param name: The index name.
        :param stats: A dict with returned CCR stats for the index.
        """

        for shard_stats in stats:
            if "shard_id" in shard_stats:
                shard_metadata = {
                    "cluster": self.cluster_name,
                    "index": name,
                    "shard": shard_stats["shard_id"],
                    "name": "ccr-stats"
                }

                self.metrics_store.put_doc(shard_stats, level=MetaInfoScope.cluster, meta_data=shard_metadata)


class NodeStats(TelemetryDevice):
    internal = False
    command = "node-stats"
    human_name = "Node Stats"
    help = "Regularly samples node stats"

    """
    Gathers different node stats.
    """
    def __init__(self, telemetry_params, clients, metrics_store):
        super().__init__()
        self.telemetry_params = telemetry_params
        self.clients = clients
        self.specified_cluster_names = self.clients.keys()
        self.metrics_store = metrics_store
        self.samplers = []

    def attach_to_cluster(self, cluster):
        # This cluster parameter does not correspond to the cluster names passed in target.hosts, see on_benchmark_start()
        super().attach_to_cluster(cluster)

    def on_benchmark_start(self):
        recorder = []
        for cluster_name in self.specified_cluster_names:
            recorder = NodeStatsRecorder(self.telemetry_params, cluster_name, self.clients[cluster_name], self.metrics_store)
            sampler = SamplerThread(recorder)
            self.samplers.append(sampler)
            sampler.setDaemon(True)
            # we don't require starting recorders precisely at the same time
            sampler.start()

    def on_benchmark_stop(self):
        if self.samplers:
            for sampler in self.samplers:
                sampler.finish()


class NodeStatsRecorder:
    def __init__(self, telemetry_params, cluster_name, client, metrics_store):
        self.sample_interval = telemetry_params.get("node-stats-sample-interval", 1)
        if self.sample_interval <= 0:
            raise exceptions.SystemSetupError(
                "The telemetry parameter 'node-stats-sample-interval' must be greater than zero but was {}.".format(self.sample_interval))

        self.include_indices = telemetry_params.get("node-stats-include-indices", False)
        self.include_indices_metrics = telemetry_params.get("node-stats-include-indices-metrics", False)

        if self.include_indices_metrics:
            if isinstance(self.include_indices_metrics, str):
                self.include_indices_metrics_list = opts.csv_to_list(self.include_indices_metrics)
            else:
                # we don't validate the allowable metrics as they may change across ES versions
                raise exceptions.SystemSetupError(
                    "The telemetry parameter 'node-stats-include-indices-metrics' must be a comma-separated string but was {}".format(
                        type(self.include_indices_metrics))
                    )
        else:
            self.include_indices_metrics_list = ["docs", "store", "indexing", "search", "merges", "query_cache",
                                                 "fielddata", "segments", "translog", "request_cache"]

        self.include_thread_pools = telemetry_params.get("node-stats-include-thread-pools", True)
        self.include_buffer_pools = telemetry_params.get("node-stats-include-buffer-pools", True)
        self.include_breakers = telemetry_params.get("node-stats-include-breakers", True)
        self.include_network = telemetry_params.get("node-stats-include-network", True)
        self.include_process = telemetry_params.get("node-stats-include-process", True)
        self.include_mem_stats = telemetry_params.get("node-stats-include-mem", True)
        self.client = client
        self.metrics_store = metrics_store
        self.metrics_store_meta_data = {"cluster": cluster_name}

    def __str__(self):
        return "node stats"

    def record(self):
        current_sample = self.sample()
        for node_stats in current_sample:
            node_name = node_stats["name"]
            collected_node_stats = collections.OrderedDict()
            collected_node_stats["name"] = "node-stats"

            if self.include_indices or self.include_indices_metrics:
                collected_node_stats.update(
                    self.indices_stats(node_name, node_stats, include=self.include_indices_metrics_list))
            if self.include_thread_pools:
                collected_node_stats.update(self.thread_pool_stats(node_name, node_stats))
            if self.include_breakers:
                collected_node_stats.update(self.circuit_breaker_stats(node_name, node_stats))
            if self.include_buffer_pools:
                collected_node_stats.update(self.jvm_buffer_pool_stats(node_name, node_stats))
            if self.include_mem_stats:
                collected_node_stats.update(self.jvm_mem_stats(node_name, node_stats))
            if self.include_network:
                collected_node_stats.update(self.network_stats(node_name, node_stats))
            if self.include_process:
                collected_node_stats.update(self.process_stats(node_name, node_stats))

            self.metrics_store.put_doc(dict(collected_node_stats),
                                       level=MetaInfoScope.node,
                                       node_name=node_name,
                                       meta_data=self.metrics_store_meta_data)

        time.sleep(self.sample_interval)

    def flatten_stats_fields(self, prefix=None, stats=None):
        """
        Flatten provided dict using an optional prefix and top level key filters.

        :param prefix: The prefix for all flattened values. Defaults to None.
        :param stats: Dict with values to be flattened, using _ as a separator. Defaults to {}.
        :return: Return flattened dictionary, separated by _ and prefixed with prefix.
        """

        def iterate():
            for section_name, section_value in stats.items():
                if isinstance(section_value, dict):
                    new_prefix = "{}_{}".format(prefix, section_name)
                    # https://www.python.org/dev/peps/pep-0380/
                    yield from self.flatten_stats_fields(prefix=new_prefix, stats=section_value).items()
                # Avoid duplication for metric fields that have unit embedded in value as they are also recorded elsewhere
                # example: `breakers_parent_limit_size_in_bytes` vs `breakers_parent_limit_size`
                elif isinstance(section_value, (int, float)) and not isinstance(section_value, bool):
                    yield "{}{}".format(prefix + "_" if prefix else "", section_name), section_value

        if stats:
            return dict(iterate())
        else:
            return dict()

    def indices_stats(self, node_name, node_stats, include):
        idx_stats = node_stats["indices"]
        ordered_results = collections.OrderedDict()
        for section in include:
            if section in idx_stats:
                ordered_results.update(self.flatten_stats_fields(prefix="indices_" + section, stats=idx_stats[section]))

        return ordered_results

    def thread_pool_stats(self, node_name, node_stats):
        return self.flatten_stats_fields(prefix="thread_pool", stats=node_stats["thread_pool"])

    def circuit_breaker_stats(self, node_name, node_stats):
        return self.flatten_stats_fields(prefix="breakers", stats=node_stats["breakers"])

    def jvm_buffer_pool_stats(self, node_name, node_stats):
        return self.flatten_stats_fields(prefix="jvm_buffer_pools", stats=node_stats["jvm"]["buffer_pools"])

    def jvm_mem_stats(self, node_name, node_stats):
        return self.flatten_stats_fields(prefix="jvm_mem", stats=node_stats["jvm"]["mem"])

    def network_stats(self, node_name, node_stats):
        return self.flatten_stats_fields(prefix="transport", stats=node_stats.get("transport"))

    def process_stats(self, node_name, node_stats):
        return self.flatten_stats_fields(prefix="process_cpu", stats=node_stats["process"]["cpu"])

    def sample(self):
        import elasticsearch
        try:
            stats = MOCK_NODE_INFO
        except elasticsearch.TransportError:
            logging.getLogger(__name__).exception("Could not retrieve node stats.")
            return {}
        return stats["nodes"].values()


class StartupTime(InternalTelemetryDevice):
    def __init__(self, metrics_store, stopwatch=time.StopWatch):
        super().__init__()
        self.metrics_store = metrics_store
        self.timer = stopwatch()

    def on_pre_node_start(self, node_name):
        self.timer.start()

    def attach_to_node(self, node):
        self.timer.stop()
        self.metrics_store.put_value_node_level(node.node_name, "node_startup_time", self.timer.total_time(), "s")


class MergeParts(InternalTelemetryDevice):
    """
    Gathers merge parts time statistics. Note that you need to run a track setup which logs these data.
    """
    MERGE_TIME_LINE = re.compile(r": (\d+) msec to merge ([a-z ]+) \[(\d+) docs\]")

    def __init__(self, metrics_store, node_log_dir):
        super().__init__()
        self.node_log_dir = node_log_dir
        self.metrics_store = metrics_store
        self._t = None
        self.node = None

    def attach_to_node(self, node):
        self.node = node

    def on_benchmark_stop(self):
        self.logger.info("Analyzing merge times.")
        # first decompress all logs. They have unique names so it's safe to do that. It's easier to first decompress everything
        for log_file in os.listdir(self.node_log_dir):
            log_path = "%s/%s" % (self.node_log_dir, log_file)
            if io.is_archive(log_path):
                self.logger.info("Decompressing [%s] to analyze merge times...", log_path)
                io.decompress(log_path, self.node_log_dir)

        # we need to add up times from all files
        merge_times = {}
        for log_file in os.listdir(self.node_log_dir):
            log_path = "%s/%s" % (self.node_log_dir, log_file)
            if not io.is_archive(log_file):
                self.logger.debug("Analyzing merge times in [%s]", log_path)
                with open(log_path, mode="rt", encoding="utf-8") as f:
                    self._extract_merge_times(f, merge_times)
            else:
                self.logger.debug("Skipping archived logs in [%s].", log_path)
        if merge_times:
            self._store_merge_times(merge_times)
        self.logger.info("Finished analyzing merge times. Extracted [%s] different merge time components.", len(merge_times))

    def _extract_merge_times(self, file, merge_times):
        for line in file.readlines():
            match = MergeParts.MERGE_TIME_LINE.search(line)
            if match is not None:
                duration_ms, part, num_docs = match.groups()
                if part not in merge_times:
                    merge_times[part] = [0, 0]
                l = merge_times[part]
                l[0] += int(duration_ms)
                l[1] += int(num_docs)

    def _store_merge_times(self, merge_times):
        for k, v in merge_times.items():
            metric_suffix = k.replace(" ", "_")
            self.metrics_store.put_value_node_level(self.node.node_name, "merge_parts_total_time_%s" % metric_suffix, v[0], "ms")
            self.metrics_store.put_count_node_level(self.node.node_name, "merge_parts_total_docs_%s" % metric_suffix, v[1])


class DiskIo(InternalTelemetryDevice):
    """
    Gathers disk I/O stats.
    """
    def __init__(self, metrics_store, node_count_on_host):
        super().__init__()
        self.metrics_store = metrics_store
        self.node_count_on_host = node_count_on_host
        self.node = None
        self.process = None
        self.disk_start = None
        self.process_start = None

    def attach_to_node(self, node):
        self.node = node
        self.process = sysstats.setup_process_stats(node.process.pid)

    def on_benchmark_start(self):
        if self.process is not None:
            self.process_start = sysstats.process_io_counters(self.process)
            if self.process_start:
                self.logger.info("Using more accurate process-based I/O counters.")
            else:
                try:
                    self.disk_start = sysstats.disk_io_counters()
                    self.logger.warning("Process I/O counters are not supported on this platform. Falling back to less accurate disk "
                                        "I/O counters.")
                except RuntimeError:
                    self.logger.exception("Could not determine I/O stats at benchmark start.")

    def on_benchmark_stop(self):
        if self.process is not None:
            # Be aware the semantics of write counts etc. are different for disk and process statistics.
            # Thus we're conservative and only report I/O bytes now.
            # noinspection PyBroadException
            try:
                # we have process-based disk counters, no need to worry how many nodes are on this host
                if self.process_start:
                    process_end = sysstats.process_io_counters(self.process)
                    read_bytes = process_end.read_bytes - self.process_start.read_bytes
                    write_bytes = process_end.write_bytes - self.process_start.write_bytes
                elif self.disk_start:
                    if self.node_count_on_host > 1:
                        self.logger.info("There are [%d] nodes on this host and Rally fell back to disk I/O counters. Attributing [1/%d] "
                                         "of total I/O to [%s].", self.node_count_on_host, self.node_count_on_host, self.node.node_name)

                    disk_end = sysstats.disk_io_counters()
                    read_bytes = (disk_end.read_bytes - self.disk_start.read_bytes) // self.node_count_on_host
                    write_bytes = (disk_end.write_bytes - self.disk_start.write_bytes) // self.node_count_on_host
                else:
                    raise RuntimeError("Neither process nor disk I/O counters are available")

                self.metrics_store.put_count_node_level(self.node.node_name, "disk_io_write_bytes", write_bytes, "byte")
                self.metrics_store.put_count_node_level(self.node.node_name, "disk_io_read_bytes", read_bytes, "byte")
            # Catching RuntimeException is not sufficient as psutil might raise AccessDenied et.al. which is derived from Exception
            except BaseException:
                self.logger.exception("Could not determine I/O stats at benchmark end.")


class CpuUsage(InternalTelemetryDevice):
    """
    Gathers CPU usage statistics.
    """
    def __init__(self, metrics_store):
        super().__init__()
        self.metrics_store = metrics_store
        self.sampler = None
        self.node = None

    def attach_to_node(self, node):
        self.node = node

    def on_benchmark_start(self):
        if self.node:
            recorder = CpuUsageRecorder(self.node, self.metrics_store)
            self.sampler = SamplerThread(recorder)
            self.sampler.setDaemon(True)
            self.sampler.start()

    def on_benchmark_stop(self):
        if self.sampler:
            self.sampler.finish()


class CpuUsageRecorder:
    def __init__(self, node, metrics_store):
        self.node = node
        self.process = sysstats.setup_process_stats(node.process.pid)
        self.metrics_store = metrics_store
        # the call is blocking already; there is no need for additional waiting in the sampler thread.
        self.sample_interval = 0

    def record(self):
        import psutil
        try:
            self.metrics_store.put_value_node_level(node_name=self.node.node_name, name="cpu_utilization_1s",
                                                    value=sysstats.cpu_utilization(self.process), unit="%")
        # this can happen when the Elasticsearch process has been terminated already and we were not quick enough to stop.
        except psutil.NoSuchProcess:
            pass

    def __str__(self):
        return "cpu utilization"


def store_node_attribute_metadata(metrics_store, nodes_info):
    # push up all node level attributes to cluster level iff the values are identical for all nodes
    pseudo_cluster_attributes = {}
    for node in nodes_info:
        if "attributes" in node:
            for k, v in node["attributes"].items():
                attribute_key = "attribute_%s" % str(k)
                metrics_store.add_meta_info(metrics.MetaInfoScope.node, node["name"], attribute_key, v)
                if attribute_key not in pseudo_cluster_attributes:
                    pseudo_cluster_attributes[attribute_key] = set()
                pseudo_cluster_attributes[attribute_key].add(v)

    for k, v in pseudo_cluster_attributes.items():
        if len(v) == 1:
            metrics_store.add_meta_info(metrics.MetaInfoScope.cluster, None, k, next(iter(v)))


def store_plugin_metadata(metrics_store, nodes_info):
    # push up all plugins to cluster level iff all nodes have the same ones
    all_nodes_plugins = []
    all_same = False

    for node in nodes_info:
        plugins = [p["name"] for p in extract_value(node, ["plugins"], fallback=[]) if "name" in p]
        if not all_nodes_plugins:
            all_nodes_plugins = plugins.copy()
            all_same = True
        else:
            # order does not matter so we do a set comparison
            all_same = all_same and set(all_nodes_plugins) == set(plugins)

        if plugins:
            metrics_store.add_meta_info(metrics.MetaInfoScope.node, node["name"], "plugins", plugins)

    if all_same and all_nodes_plugins:
        metrics_store.add_meta_info(metrics.MetaInfoScope.cluster, None, "plugins", all_nodes_plugins)


def extract_value(node, path, fallback="unknown"):
    value = node
    try:
        for k in path:
            value = value[k]
    except KeyError:
        value = fallback
    return value


class ClusterEnvironmentInfo(InternalTelemetryDevice):
    """
    Gathers static environment information on a cluster level (e.g. version numbers).
    """
    def __init__(self, client, metrics_store):
        super().__init__()
        self.metrics_store = metrics_store
        self.client = client

    def attach_to_cluster(self, cluster):
        client_info = self.client.info()
        revision = client_info["version"]["build_hash"]
        distribution_version = client_info["version"]["number"]
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.cluster, None, "source_revision", revision)
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.cluster, None, "distribution_version", distribution_version)

        info = MOCK_NODE_INFO
        nodes_info = info["nodes"].values()
        for node in nodes_info:
            node_name = node["name"]
            # while we could determine this for bare-metal nodes that are provisioned by Rally, there are other cases (Docker, externally
            # provisioned clusters) where it's not that easy.
            self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node_name, "jvm_vendor", extract_value(node, ["jvm", "vm_vendor"]))
            self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node_name, "jvm_version", extract_value(node, ["jvm", "version"]))

        store_plugin_metadata(self.metrics_store, nodes_info)
        store_node_attribute_metadata(self.metrics_store, nodes_info)


class NodeEnvironmentInfo(InternalTelemetryDevice):
    """
    Gathers static environment information like OS or CPU details for Rally-provisioned nodes.
    """
    def __init__(self, metrics_store):
        super().__init__()
        self.metrics_store = metrics_store

    def attach_to_node(self, node):
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node.node_name, "os_name", sysstats.os_name())
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node.node_name, "os_version", sysstats.os_version())
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node.node_name, "cpu_logical_cores", sysstats.logical_cpu_cores())
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node.node_name, "cpu_physical_cores", sysstats.physical_cpu_cores())
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node.node_name, "cpu_model", sysstats.cpu_model())
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node.node_name, "node_name", node.node_name)
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node.node_name, "host_name", node.host_name)


class ExternalEnvironmentInfo(InternalTelemetryDevice):
    """
    Gathers static environment information for externally provisioned clusters.
    """
    def __init__(self, client, metrics_store):
        super().__init__()
        self.metrics_store = metrics_store
        self.client = client
        self._t = None

    def attach_to_cluster(self, cluster):
        stats = MOCK_NODE_INFO
        nodes = stats["nodes"]
        for node in nodes.values():
            node_name = node["name"]
            host = node.get("host", "unknown")
            self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node_name, "node_name", node_name)
            self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node_name, "host_name", host)

        info = MOCK_NODE_INFO
        nodes_info = info["nodes"].values()
        for node in nodes_info:
            node_name = node["name"]
            self.store_node_info(node_name, "os_name", node, ["os", "name"])
            self.store_node_info(node_name, "os_version", node, ["os", "version"])
            self.store_node_info(node_name, "cpu_logical_cores", node, ["os", "available_processors"])
            self.store_node_info(node_name, "jvm_vendor", node, ["jvm", "vm_vendor"])
            self.store_node_info(node_name, "jvm_version", node, ["jvm", "version"])

        store_plugin_metadata(self.metrics_store, nodes_info)
        store_node_attribute_metadata(self.metrics_store, nodes_info)

    def store_node_info(self, node_name, metric_key, node, path):
        self.metrics_store.add_meta_info(metrics.MetaInfoScope.node, node_name, metric_key, extract_value(node, path))


class ClusterMetaDataInfo(InternalTelemetryDevice):
    """
    Enriches the cluster with meta-data about it and its nodes.
    """
    def __init__(self, client):
        super().__init__()
        self.client = client

    def attach_to_cluster(self, cluster):
        client_info = self.client.info()
        revision = client_info["version"]["build_hash"]
        distribution_version = client_info["version"]["number"]

        cluster.distribution_version = distribution_version
        cluster.source_revision = revision

        for node_stats in MOCK_NODE_INFO["nodes"].values():
            node_name = node_stats["name"]
            if cluster.has_node(node_name):
                cluster_node = cluster.node(node_name)
            else:
                host = node_stats.get("host", "unknown")
                cluster_node = cluster.add_node(host, node_name)
            self.add_node_stats(cluster, cluster_node, node_stats)

        for node_info in MOCK_NODE_INFO["nodes"].values():
            self.add_node_info(cluster, node_info)

    def add_node_info(self, cluster, node_info):
        node_name = node_info["name"]
        cluster_node = cluster.node(node_name)
        if cluster_node:
            cluster_node.ip = extract_value(node_info, ["ip"])
            cluster_node.os = {
                "name": extract_value(node_info, ["os", "name"]),
                "version": extract_value(node_info, ["os", "version"])
            }
            cluster_node.jvm = {
                "vendor": extract_value(node_info, ["jvm", "vm_vendor"]),
                "version": extract_value(node_info, ["jvm", "version"])
            }
            cluster_node.cpu = {
                "available_processors": extract_value(node_info, ["os", "available_processors"]),
                "allocated_processors": extract_value(node_info, ["os", "allocated_processors"], fallback=None),
            }
            for plugin in extract_value(node_info, ["plugins"], fallback=[]):
                if "name" in plugin:
                    cluster_node.plugins.append(plugin["name"])

            if versions.major_version(cluster.distribution_version) == 1:
                cluster_node.memory = {
                    "total_bytes": extract_value(node_info, ["os", "mem", "total_in_bytes"], fallback=None)
                }

    def add_node_stats(self, cluster, cluster_node, stats):
        if cluster_node:
            data_dirs = extract_value(stats, ["fs", "data"], fallback=[])
            for data_dir in data_dirs:
                fs_meta_data = {
                    "mount": data_dir.get("mount", "unknown"),
                    "type": data_dir.get("type", "unknown"),
                    "spins": data_dir.get("spins", "unknown")
                }
                cluster_node.fs.append(fs_meta_data)
            if versions.major_version(cluster.distribution_version) > 1:
                cluster_node.memory = {
                    "total_bytes": extract_value(stats, ["os", "mem", "total_in_bytes"], fallback=None)
                }


class GcTimesSummary(InternalTelemetryDevice):
    """
    Gathers a summary of the total young gen/old gen GC runtime during the whole race.
    """
    def __init__(self, client, metrics_store):
        super().__init__()
        self.metrics_store = metrics_store
        self.client = client
        self.gc_times_per_node = {}

    def on_benchmark_start(self):
        self.gc_times_per_node = self.gc_times()

    def on_benchmark_stop(self):
        gc_times_at_end = self.gc_times()
        total_old_gen_collection_time = 0
        total_young_gen_collection_time = 0

        for node_name, gc_times_end in gc_times_at_end.items():
            if node_name in self.gc_times_per_node:
                gc_times_start = self.gc_times_per_node[node_name]
                young_gc_time = max(gc_times_end[0] - gc_times_start[0], 0)
                old_gc_time = max(gc_times_end[1] - gc_times_start[1], 0)

                total_young_gen_collection_time += young_gc_time
                total_old_gen_collection_time += old_gc_time

                self.metrics_store.put_value_node_level(node_name, "node_young_gen_gc_time", young_gc_time, "ms")
                self.metrics_store.put_value_node_level(node_name, "node_old_gen_gc_time", old_gc_time, "ms")
            else:
                self.logger.warning("Cannot determine GC times for [%s] (not in the cluster at the start of the benchmark).", node_name)

        self.metrics_store.put_value_cluster_level("node_total_young_gen_gc_time", total_young_gen_collection_time, "ms")
        self.metrics_store.put_value_cluster_level("node_total_old_gen_gc_time", total_old_gen_collection_time, "ms")

        self.gc_times_per_node = None

    def gc_times(self):
        self.logger.debug("Gathering GC times")
        gc_times = {}
        import elasticsearch
        try:
            stats = MOCK_NODE_INFO
        except elasticsearch.TransportError:
            self.logger.exception("Could not retrieve GC times.")
            return gc_times
        nodes = stats["nodes"]
        for node in nodes.values():
            node_name = node["name"]
            gc = node["jvm"]["gc"]["collectors"]
            old_gen_collection_time = gc["old"]["collection_time_in_millis"]
            young_gen_collection_time = gc["young"]["collection_time_in_millis"]
            gc_times[node_name] = (young_gen_collection_time, old_gen_collection_time)
        return gc_times


class IndexStats(InternalTelemetryDevice):
    """
    Gathers statistics via the Elasticsearch index stats API
    """
    def __init__(self, client, metrics_store):
        super().__init__()
        self.client = client
        self.metrics_store = metrics_store
        self.first_time = True

    def on_benchmark_start(self):
        # we only determine this value at the start of the benchmark (in the first lap). This is actually only useful for
        # the pipeline "benchmark-only" where we don't have control over the cluster and the user might not have restarted
        # the cluster so we can at least tell them.
        if self.first_time:
            for t in self.index_times(self.index_stats(), per_shard_stats=False):
                n = t["name"]
                v = t["value"]
                if t["value"] > 0:
                    console.warn("%s is %d ms indicating that the cluster is not in a defined clean state. Recorded index time "
                                 "metrics may be misleading." % (n, v), logger=self.logger)
            self.first_time = False

    def on_benchmark_stop(self):
        self.logger.info("Gathering indices stats for all primaries on benchmark stop.")
        index_stats = self.index_stats()
        # import json
        # self.logger.debug("Returned indices stats:\n%s", json.dumps(index_stats, indent=2))
        if "_all" not in index_stats or "primaries" not in index_stats["_all"]:
            return
        p = index_stats["_all"]["primaries"]
        # actually this is add_count
        self.add_metrics(self.extract_value(p, ["segments", "count"]), "segments_count")
        self.add_metrics(self.extract_value(p, ["segments", "memory_in_bytes"]), "segments_memory_in_bytes", "byte")

        for t in self.index_times(index_stats):
            self.metrics_store.put_doc(doc=t, level=metrics.MetaInfoScope.cluster)

        self.add_metrics(self.extract_value(p, ["segments", "doc_values_memory_in_bytes"]), "segments_doc_values_memory_in_bytes", "byte")
        self.add_metrics(self.extract_value(p, ["segments", "stored_fields_memory_in_bytes"]), "segments_stored_fields_memory_in_bytes", "byte")
        self.add_metrics(self.extract_value(p, ["segments", "terms_memory_in_bytes"]), "segments_terms_memory_in_bytes", "byte")
        self.add_metrics(self.extract_value(p, ["segments", "norms_memory_in_bytes"]), "segments_norms_memory_in_bytes", "byte")
        self.add_metrics(self.extract_value(p, ["segments", "points_memory_in_bytes"]), "segments_points_memory_in_bytes", "byte")
        self.add_metrics(self.extract_value(index_stats, ["_all", "total", "store", "size_in_bytes"]), "store_size_in_bytes", "byte")
        self.add_metrics(self.extract_value(index_stats, ["_all", "total", "translog", "size_in_bytes"]), "translog_size_in_bytes", "byte")

    def index_stats(self):
        # noinspection PyBroadException
        try:
            return self.client.indices.stats(metric="_all", level="shards")
        except BaseException:
            self.logger.exception("Could not retrieve index stats.")
            return {}

    def index_times(self, stats, per_shard_stats=True):
        times = []
        self.index_time(times, stats, "merges_total_time", ["merges", "total_time_in_millis"], per_shard_stats),
        self.index_time(times, stats, "merges_total_throttled_time", ["merges", "total_throttled_time_in_millis"], per_shard_stats),
        self.index_time(times, stats, "indexing_total_time", ["indexing", "index_time_in_millis"], per_shard_stats),
        self.index_time(times, stats, "indexing_throttle_time", ["indexing", "throttle_time_in_millis"], per_shard_stats),
        self.index_time(times, stats, "refresh_total_time", ["refresh", "total_time_in_millis"], per_shard_stats),
        self.index_time(times, stats, "flush_total_time", ["flush", "total_time_in_millis"], per_shard_stats),
        return times

    def index_time(self, values, stats, name, path, per_shard_stats):
        primary_total_stats = self.extract_value(stats, ["_all", "primaries"], default_value={})
        value = self.extract_value(primary_total_stats, path)
        if value:
            doc = {
                "name": name,
                "value": value,
                "unit": "ms",
            }
            if per_shard_stats:
                doc["per-shard"] = self.primary_shard_stats(stats, path)
            values.append(doc)

    def primary_shard_stats(self, stats, path):
        shard_stats = []
        try:
            for idx, shards in stats["indices"].items():
                for shard_number, shard in shards["shards"].items():
                    for shard_metrics in shard:
                        if shard_metrics["routing"]["primary"]:
                            shard_stats.append(self.extract_value(shard_metrics, path, default_value=0))
        except KeyError:
            self.logger.warning("Could not determine primary shard stats at path [%s].", ",".join(path))
        return shard_stats

    def add_metrics(self, value, metric_key, unit=None):
        if value is not None:
            if unit:
                self.metrics_store.put_value_cluster_level(metric_key, value, unit)
            else:
                self.metrics_store.put_count_cluster_level(metric_key, value)

    def extract_value(self, primaries, path, default_value=None):
        value = primaries
        try:
            for k in path:
                value = value[k]
            return value
        except KeyError:
            self.logger.warning("Could not determine value at path [%s]. Returning default value [%s]", ",".join(path), str(default_value))
            return default_value


class MlBucketProcessingTime(InternalTelemetryDevice):
    def __init__(self, client, metrics_store):
        super().__init__()
        self.client = client
        self.metrics_store = metrics_store

    def detach_from_cluster(self, cluster):
        import elasticsearch
        try:
            results = self.client.search(index=".ml-anomalies-*", body={
                "size": 0,
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"result_type": "bucket"}}
                        ]
                    }
                },
                "aggs": {
                    "jobs": {
                        "terms": {
                            "field": "job_id"
                        },
                        "aggs": {
                            "min_pt": {
                                "min": {"field": "processing_time_ms"}
                            },
                            "max_pt": {
                                "max": {"field": "processing_time_ms"}
                            },
                            "mean_pt": {
                                "avg": {"field": "processing_time_ms"}
                            },
                            "median_pt": {
                                "percentiles": {"field": "processing_time_ms", "percents": [50]}
                            }
                        }
                    }
                }
            })
        except elasticsearch.TransportError:
            self.logger.exception("Could not retrieve ML bucket processing time.")
            return
        try:
            for job in results["aggregations"]["jobs"]["buckets"]:
                ml_job_stats = collections.OrderedDict()
                ml_job_stats["name"] = "ml_processing_time"
                ml_job_stats["job"] = job["key"]
                ml_job_stats["min"] = job["min_pt"]["value"]
                ml_job_stats["mean"] = job["mean_pt"]["value"]
                ml_job_stats["median"] = job["median_pt"]["values"]["50.0"]
                ml_job_stats["max"] = job["max_pt"]["value"]
                ml_job_stats["unit"] = "ms"
                self.metrics_store.put_doc(doc=dict(ml_job_stats), level=MetaInfoScope.cluster)
        except KeyError:
            # no ML running
            pass


class IndexSize(InternalTelemetryDevice):
    """
    Measures the final size of the index
    """
    def __init__(self, data_paths, metrics_store):
        super().__init__()
        self.data_paths = data_paths
        self.metrics_store = metrics_store
        self.attached = False

    def attach_to_node(self, node):
        self.attached = True

    def detach_from_node(self, node, running):
        # we need to gather the file size after the node has terminated so we can be sure that it has written all its buffers.
        if not running and self.attached and self.data_paths:
            self.attached = False
            index_size_bytes = 0
            for data_path in self.data_paths:
                index_size_bytes += io.get_size(data_path)
            self.metrics_store.put_count_node_level(node.node_name, "final_index_size_bytes", index_size_bytes, "byte")
