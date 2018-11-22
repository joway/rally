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

MOCK_SHARDS_INFO = json.loads("""
{
  "_shards": {
    "total": 130,
    "successful": 130,
    "failed": 0
  },
  "_all": {
    "primaries": {
      "docs": {
        "count": 6085848331,
        "deleted": 4586
      },
      "store": {
        "size_in_bytes": 2936191341261
      },
      "indexing": {
        "index_total": 6087749686,
        "index_time_in_millis": 1207814413,
        "index_current": 8,
        "index_failed": 0,
        "delete_total": 0,
        "delete_time_in_millis": 0,
        "delete_current": 0,
        "noop_update_total": 0,
        "is_throttled": false,
        "throttle_time_in_millis": 0
      },
      "get": {
        "total": 23457,
        "time_in_millis": 1848,
        "exists_total": 11897,
        "exists_time_in_millis": 1040,
        "missing_total": 11560,
        "missing_time_in_millis": 808,
        "current": 0
      },
      "search": {
        "open_contexts": 0,
        "query_total": 299840,
        "query_time_in_millis": 24372848,
        "query_current": 0,
        "fetch_total": 91518,
        "fetch_time_in_millis": 29850,
        "fetch_current": 0,
        "scroll_total": 0,
        "scroll_time_in_millis": 0,
        "scroll_current": 0,
        "suggest_total": 0,
        "suggest_time_in_millis": 0,
        "suggest_current": 0
      },
      "merges": {
        "current": 13,
        "current_docs": 42880229,
        "current_size_in_bytes": 17774716110,
        "total": 164763,
        "total_time_in_millis": 3146954789,
        "total_docs": 18608696101,
        "total_size_in_bytes": 10773745204657,
        "total_stopped_time_in_millis": 213377,
        "total_throttled_time_in_millis": 2413910629,
        "total_auto_throttle_in_bytes": 1020322423
      },
      "refresh": {
        "total": 861834,
        "total_time_in_millis": 227090392,
        "listeners": 0
      },
      "flush": {
        "total": 14573,
        "periodic": 14500,
        "total_time_in_millis": 13970468
      },
      "warmer": {
        "current": 0,
        "total": 823466,
        "total_time_in_millis": 173906
      },
      "query_cache": {
        "memory_size_in_bytes": 422316873,
        "total_count": 625813,
        "hit_count": 335819,
        "miss_count": 289994,
        "cache_size": 1066,
        "cache_count": 4116,
        "evictions": 3050
      },
      "fielddata": {
        "memory_size_in_bytes": 920,
        "evictions": 0
      },
      "completion": {
        "size_in_bytes": 0
      },
      "segments": {
        "count": 2613,
        "memory_in_bytes": 6697013698,
        "terms_memory_in_bytes": 5384399410,
        "stored_fields_memory_in_bytes": 1164152848,
        "term_vectors_memory_in_bytes": 0,
        "norms_memory_in_bytes": 1472,
        "points_memory_in_bytes": 136280412,
        "doc_values_memory_in_bytes": 12179556,
        "index_writer_memory_in_bytes": 167223084,
        "version_map_memory_in_bytes": 0,
        "fixed_bit_set_memory_in_bytes": 10896,
        "max_unsafe_auto_id_timestamp": 1542844802019,
        "file_sizes": {

        }
      },
      "translog": {
        "operations": 22364220,
        "size_in_bytes": 22743995467,
        "uncommitted_operations": 6178684,
        "uncommitted_size_in_bytes": 5420721267,
        "earliest_last_modified_age": 0
      },
      "request_cache": {
        "memory_size_in_bytes": 848,
        "evictions": 0,
        "hit_count": 36373,
        "miss_count": 7585
      },
      "recovery": {
        "current_as_source": 0,
        "current_as_target": 0,
        "throttle_time_in_millis": 798
      }
    },
    "total": {
      "docs": {
        "count": 6096922743,
        "deleted": 9014
      },
      "store": {
        "size_in_bytes": 2944315227525
      },
      "indexing": {
        "index_total": 6099904750,
        "index_time_in_millis": 1212696486,
        "index_current": 8,
        "index_failed": 0,
        "delete_total": 0,
        "delete_time_in_millis": 0,
        "delete_current": 0,
        "noop_update_total": 0,
        "is_throttled": false,
        "throttle_time_in_millis": 0
      },
      "get": {
        "total": 47181,
        "time_in_millis": 3886,
        "exists_total": 23724,
        "exists_time_in_millis": 2041,
        "missing_total": 23457,
        "missing_time_in_millis": 1845,
        "current": 0
      },
      "search": {
        "open_contexts": 0,
        "query_total": 439875,
        "query_time_in_millis": 24428692,
        "query_current": 0,
        "fetch_total": 179207,
        "fetch_time_in_millis": 34980,
        "fetch_current": 0,
        "scroll_total": 0,
        "scroll_time_in_millis": 0,
        "scroll_current": 0,
        "suggest_total": 0,
        "suggest_time_in_millis": 0,
        "suggest_current": 0
      },
      "merges": {
        "current": 13,
        "current_docs": 42880229,
        "current_size_in_bytes": 17774716110,
        "total": 213216,
        "total_time_in_millis": 3157188197,
        "total_docs": 18746227586,
        "total_size_in_bytes": 10904621392984,
        "total_stopped_time_in_millis": 213377,
        "total_throttled_time_in_millis": 2414175337,
        "total_auto_throttle_in_bytes": 1783702712
      },
      "refresh": {
        "total": 1257748,
        "total_time_in_millis": 238719647,
        "listeners": 0
      },
      "flush": {
        "total": 14638,
        "periodic": 14527,
        "total_time_in_millis": 13980036
      },
      "warmer": {
        "current": 0,
        "total": 1197518,
        "total_time_in_millis": 315213
      },
      "query_cache": {
        "memory_size_in_bytes": 422316873,
        "total_count": 835803,
        "hit_count": 363147,
        "miss_count": 472656,
        "cache_size": 1066,
        "cache_count": 5844,
        "evictions": 4778
      },
      "fielddata": {
        "memory_size_in_bytes": 1840,
        "evictions": 0
      },
      "completion": {
        "size_in_bytes": 0
      },
      "segments": {
        "count": 3128,
        "memory_in_bytes": 6720761484,
        "terms_memory_in_bytes": 5391570949,
        "stored_fields_memory_in_bytes": 1167175464,
        "term_vectors_memory_in_bytes": 0,
        "norms_memory_in_bytes": 2944,
        "points_memory_in_bytes": 138139431,
        "doc_values_memory_in_bytes": 23872696,
        "index_writer_memory_in_bytes": 197748372,
        "version_map_memory_in_bytes": 0,
        "fixed_bit_set_memory_in_bytes": 21768,
        "max_unsafe_auto_id_timestamp": 1542862101307,
        "file_sizes": {

        }
      },
      "translog": {
        "operations": 25496732,
        "size_in_bytes": 27356356280,
        "uncommitted_operations": 6830106,
        "uncommitted_size_in_bytes": 6459915071,
        "earliest_last_modified_age": 0
      },
      "request_cache": {
        "memory_size_in_bytes": 1696,
        "evictions": 0,
        "hit_count": 72546,
        "miss_count": 15168
      },
      "recovery": {
        "current_as_source": 0,
        "current_as_target": 0,
        "throttle_time_in_millis": 3876
      }
    }
  },
  "indices": {
    ".monitoring-kibana-6-2018.11.20": {
      "uuid": "5Rd4mGFAStabs7xnb6PUsw",
      "primaries": {
        "docs": {
          "count": 8637,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2404949
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 12,
          "query_time_in_millis": 0,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 3,
          "total_time_in_millis": 0,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 1,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 5,
          "memory_in_bytes": 31875,
          "terms_memory_in_bytes": 22966,
          "stored_fields_memory_in_bytes": 1960,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 1385,
          "doc_values_memory_in_bytes": 5564,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542758394875,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 110,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 17274,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 4809909
        },
        "indexing": {
          "index_total": 8636,
          "index_time_in_millis": 25593,
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
          "query_total": 79,
          "query_time_in_millis": 71,
          "query_current": 0,
          "fetch_total": 4,
          "fetch_time_in_millis": 7,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 959,
          "total_time_in_millis": 94614,
          "total_docs": 2074895,
          "total_size_in_bytes": 714534529,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 9604,
          "total_time_in_millis": 147580,
          "listeners": 0
        },
        "flush": {
          "total": 3,
          "periodic": 0,
          "total_time_in_millis": 25
        },
        "warmer": {
          "current": 0,
          "total": 9599,
          "total_time_in_millis": 382
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 10,
          "memory_in_bytes": 63750,
          "terms_memory_in_bytes": 45932,
          "stored_fields_memory_in_bytes": 3920,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 2770,
          "doc_values_memory_in_bytes": 11128,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542758394875,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 165,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 165,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 27,
          "miss_count": 13
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 8637,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2404960
            },
            "indexing": {
              "index_total": 8636,
              "index_time_in_millis": 25593,
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
              "query_total": 67,
              "query_time_in_millis": 71,
              "query_current": 0,
              "fetch_total": 4,
              "fetch_time_in_millis": 7,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 959,
              "total_time_in_millis": 94614,
              "total_docs": 2074895,
              "total_size_in_bytes": 714534529,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 9601,
              "total_time_in_millis": 147580,
              "listeners": 0
            },
            "flush": {
              "total": 2,
              "periodic": 0,
              "total_time_in_millis": 25
            },
            "warmer": {
              "current": 0,
              "total": 9598,
              "total_time_in_millis": 382
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 5,
              "memory_in_bytes": 31875,
              "terms_memory_in_bytes": 22966,
              "stored_fields_memory_in_bytes": 1960,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1385,
              "doc_values_memory_in_bytes": 5564,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672006847,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108693460
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 27,
              "miss_count": 13
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBurzA==",
              "generation": 5,
              "user_data": {
                "local_checkpoint": "8636",
                "max_unsafe_auto_id_timestamp": "1542672006847",
                "translog_uuid": "87187q5gQ0qSgze6LW8w8Q",
                "history_uuid": "cpmMpxC2TVimO9J8A7NnLg",
                "sync_id": "7eBZWA4iS5S7LtUu6dfmuw",
                "translog_generation": "3",
                "max_seq_no": "8636"
              },
              "num_docs": 8637
            },
            "seq_no": {
              "max_seq_no": 8636,
              "local_checkpoint": 8636,
              "global_checkpoint": 8636
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 8637,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2404949
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 12,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 0,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 5,
              "memory_in_bytes": 31875,
              "terms_memory_in_bytes": 22966,
              "stored_fields_memory_in_bytes": 1960,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1385,
              "doc_values_memory_in_bytes": 5564,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758394875,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 110,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 110,
              "earliest_last_modified_age": 18989085
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsA7ng==",
              "generation": 5,
              "user_data": {
                "local_checkpoint": "8636",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "jgzfTIrOSla4cqt2cDp9-g",
                "history_uuid": "cpmMpxC2TVimO9J8A7NnLg",
                "sync_id": "7eBZWA4iS5S7LtUu6dfmuw",
                "translog_generation": "1",
                "max_seq_no": "8636"
              },
              "num_docs": 8637
            },
            "seq_no": {
              "max_seq_no": 8636,
              "local_checkpoint": 8636,
              "global_checkpoint": 8636
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-kibana-6-2018.11.21": {
      "uuid": "X3AKMtVURhKl74ikUD9QjA",
      "primaries": {
        "docs": {
          "count": 8637,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2419147
        },
        "indexing": {
          "index_total": 8637,
          "index_time_in_millis": 18131,
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
          "query_total": 35,
          "query_time_in_millis": 69,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 959,
          "total_time_in_millis": 85093,
          "total_docs": 2074846,
          "total_size_in_bytes": 724189835,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 9601,
          "total_time_in_millis": 126268,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 23
        },
        "warmer": {
          "current": 0,
          "total": 9598,
          "total_time_in_millis": 314
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 5,
          "memory_in_bytes": 34383,
          "terms_memory_in_bytes": 23046,
          "stored_fields_memory_in_bytes": 2040,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 1381,
          "doc_values_memory_in_bytes": 7916,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 8637,
          "size_in_bytes": 13530140,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 55,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 2,
          "miss_count": 25
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 17274,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 4855055
        },
        "indexing": {
          "index_total": 17273,
          "index_time_in_millis": 40389,
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
          "query_total": 76,
          "query_time_in_millis": 119,
          "query_current": 0,
          "fetch_total": 4,
          "fetch_time_in_millis": 5,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 1918,
          "total_time_in_millis": 167788,
          "total_docs": 4147677,
          "total_size_in_bytes": 1447766770,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 19201,
          "total_time_in_millis": 257755,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 48
        },
        "warmer": {
          "current": 0,
          "total": 19196,
          "total_time_in_millis": 675
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 11,
          "memory_in_bytes": 73633,
          "terms_memory_in_bytes": 50616,
          "stored_fields_memory_in_bytes": 4376,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 2805,
          "doc_values_memory_in_bytes": 15836,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542758405934,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 17274,
          "size_in_bytes": 27060280,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 2,
          "miss_count": 46
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 8637,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2419147
            },
            "indexing": {
              "index_total": 8637,
              "index_time_in_millis": 18131,
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
              "query_total": 35,
              "query_time_in_millis": 69,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 959,
              "total_time_in_millis": 85093,
              "total_docs": 2074846,
              "total_size_in_bytes": 724189835,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 9601,
              "total_time_in_millis": 126268,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 23
            },
            "warmer": {
              "current": 0,
              "total": 9598,
              "total_time_in_millis": 314
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 5,
              "memory_in_bytes": 34383,
              "terms_memory_in_bytes": 23046,
              "stored_fields_memory_in_bytes": 2040,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1381,
              "doc_values_memory_in_bytes": 7916,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 8637,
              "size_in_bytes": 13530140,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22592721
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 2,
              "miss_count": 25
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO813A==",
              "generation": 4,
              "user_data": {
                "local_checkpoint": "8636",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "wI4FGvkSR7yHmoNJiFE77Q",
                "history_uuid": "gmiND46qQpOStacYFCMzbQ",
                "sync_id": "mXeKndEbSt6mbLA3cS_ezg",
                "translog_generation": "3",
                "max_seq_no": "8636"
              },
              "num_docs": 8637
            },
            "seq_no": {
              "max_seq_no": 8636,
              "local_checkpoint": 8636,
              "global_checkpoint": 8636
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 8637,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2435908
            },
            "indexing": {
              "index_total": 8636,
              "index_time_in_millis": 22258,
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
              "query_total": 41,
              "query_time_in_millis": 50,
              "query_current": 0,
              "fetch_total": 4,
              "fetch_time_in_millis": 5,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 959,
              "total_time_in_millis": 82695,
              "total_docs": 2072831,
              "total_size_in_bytes": 723576935,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 9600,
              "total_time_in_millis": 131487,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 25
            },
            "warmer": {
              "current": 0,
              "total": 9598,
              "total_time_in_millis": 361
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 6,
              "memory_in_bytes": 39250,
              "terms_memory_in_bytes": 27570,
              "stored_fields_memory_in_bytes": 2336,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1424,
              "doc_values_memory_in_bytes": 7920,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758405934,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 8637,
              "size_in_bytes": 13530140,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22592081
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 21
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB63BQ==",
              "generation": 5,
              "user_data": {
                "local_checkpoint": "8636",
                "max_unsafe_auto_id_timestamp": "1542758405934",
                "translog_uuid": "h5i3iuw6T0uoAg6SDmnmtw",
                "history_uuid": "gmiND46qQpOStacYFCMzbQ",
                "sync_id": "mXeKndEbSt6mbLA3cS_ezg",
                "translog_generation": "3",
                "max_seq_no": "8636"
              },
              "num_docs": 8637
            },
            "seq_no": {
              "max_seq_no": 8636,
              "local_checkpoint": 8636,
              "global_checkpoint": 8636
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-kibana-6-2018.11.22": {
      "uuid": "eZndP82qTNWAD6lWYCDR7w",
      "primaries": {
        "docs": {
          "count": 2169,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 1325374
        },
        "indexing": {
          "index_total": 2169,
          "index_time_in_millis": 4792,
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
          "query_total": 7,
          "query_time_in_millis": 0,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 240,
          "total_time_in_millis": 8055,
          "total_docs": 130929,
          "total_size_in_bytes": 75962528,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 2419,
          "total_time_in_millis": 30190,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 48
        },
        "warmer": {
          "current": 0,
          "total": 2414,
          "total_time_in_millis": 86
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 9,
          "memory_in_bytes": 46435,
          "terms_memory_in_bytes": 41076,
          "stored_fields_memory_in_bytes": 2872,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 819,
          "doc_values_memory_in_bytes": 1668,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 2169,
          "size_in_bytes": 3394816,
          "uncommitted_operations": 459,
          "uncommitted_size_in_bytes": 718876,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 4338,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2650759
        },
        "indexing": {
          "index_total": 4337,
          "index_time_in_millis": 9898,
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
          "query_total": 23,
          "query_time_in_millis": 1,
          "query_current": 0,
          "fetch_total": 1,
          "fetch_time_in_millis": 23,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 480,
          "total_time_in_millis": 16686,
          "total_docs": 261858,
          "total_size_in_bytes": 151925056,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 4837,
          "total_time_in_millis": 62855,
          "listeners": 0
        },
        "flush": {
          "total": 4,
          "periodic": 0,
          "total_time_in_millis": 593
        },
        "warmer": {
          "current": 0,
          "total": 4828,
          "total_time_in_millis": 185
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 18,
          "memory_in_bytes": 92870,
          "terms_memory_in_bytes": 82152,
          "stored_fields_memory_in_bytes": 5744,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 1638,
          "doc_values_memory_in_bytes": 3336,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542844807047,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 4338,
          "size_in_bytes": 6789632,
          "uncommitted_operations": 918,
          "uncommitted_size_in_bytes": 1437752,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 2169,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 1325374
            },
            "indexing": {
              "index_total": 2169,
              "index_time_in_millis": 4792,
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
              "query_total": 7,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 240,
              "total_time_in_millis": 8055,
              "total_docs": 130929,
              "total_size_in_bytes": 75962528,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 2419,
              "total_time_in_millis": 30190,
              "listeners": 0
            },
            "flush": {
              "total": 2,
              "periodic": 0,
              "total_time_in_millis": 48
            },
            "warmer": {
              "current": 0,
              "total": 2414,
              "total_time_in_millis": 86
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 9,
              "memory_in_bytes": 46435,
              "terms_memory_in_bytes": 41076,
              "stored_fields_memory_in_bytes": 2872,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 819,
              "doc_values_memory_in_bytes": 1668,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 2169,
              "size_in_bytes": 3394816,
              "uncommitted_operations": 459,
              "uncommitted_size_in_bytes": 718876,
              "earliest_last_modified_age": 22582438
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO/GKA==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "1709",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "EwRCGtHmSve7GvMP2JBzKA",
                "history_uuid": "rsvh2XgYT5-D2MPOseZWFQ",
                "sync_id": "BGw6Tfw0TCKYwMz5zfFJDQ",
                "translog_generation": "4",
                "max_seq_no": "1709"
              },
              "num_docs": 1710
            },
            "seq_no": {
              "max_seq_no": 2168,
              "local_checkpoint": 2168,
              "global_checkpoint": 2168
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 2169,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 1325385
            },
            "indexing": {
              "index_total": 2168,
              "index_time_in_millis": 5106,
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
              "query_total": 16,
              "query_time_in_millis": 1,
              "query_current": 0,
              "fetch_total": 1,
              "fetch_time_in_millis": 23,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 240,
              "total_time_in_millis": 8631,
              "total_docs": 130929,
              "total_size_in_bytes": 75962528,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 2418,
              "total_time_in_millis": 32665,
              "listeners": 0
            },
            "flush": {
              "total": 2,
              "periodic": 0,
              "total_time_in_millis": 545
            },
            "warmer": {
              "current": 0,
              "total": 2414,
              "total_time_in_millis": 99
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 9,
              "memory_in_bytes": 46435,
              "terms_memory_in_bytes": 41076,
              "stored_fields_memory_in_bytes": 2872,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 819,
              "doc_values_memory_in_bytes": 1668,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844807047,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 2169,
              "size_in_bytes": 3394816,
              "uncommitted_operations": 459,
              "uncommitted_size_in_bytes": 718876,
              "earliest_last_modified_age": 22582314
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB9PpQ==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "1709",
                "max_unsafe_auto_id_timestamp": "1542844807047",
                "translog_uuid": "4yaaz68STECHOAyr5zqlrg",
                "history_uuid": "rsvh2XgYT5-D2MPOseZWFQ",
                "sync_id": "BGw6Tfw0TCKYwMz5zfFJDQ",
                "translog_generation": "4",
                "max_seq_no": "1709"
              },
              "num_docs": 1710
            },
            "seq_no": {
              "max_seq_no": 2168,
              "local_checkpoint": 2168,
              "global_checkpoint": 2168
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-es-6-2018.11.20": {
      "uuid": "KK07gPywQTaGe7ApuGLz3A",
      "primaries": {
        "docs": {
          "count": 271388,
          "deleted": 1170
        },
        "store": {
          "size_in_bytes": 197803546
        },
        "indexing": {
          "index_total": 1198856,
          "index_time_in_millis": 363564,
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
          "query_total": 9195,
          "query_time_in_millis": 10196,
          "query_current": 0,
          "fetch_total": 710,
          "fetch_time_in_millis": 706,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 4778,
          "total_time_in_millis": 1397023,
          "total_docs": 13870956,
          "total_size_in_bytes": 12354236835,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 160,
          "total_auto_throttle_in_bytes": 17331834
        },
        "refresh": {
          "total": 46569,
          "total_time_in_millis": 800841,
          "listeners": 0
        },
        "flush": {
          "total": 3,
          "periodic": 2,
          "total_time_in_millis": 375
        },
        "warmer": {
          "current": 0,
          "total": 37925,
          "total_time_in_millis": 26469
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 32318,
          "hit_count": 1939,
          "miss_count": 30379,
          "cache_size": 0,
          "cache_count": 989,
          "evictions": 989
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 16,
          "memory_in_bytes": 449754,
          "terms_memory_in_bytes": 127677,
          "stored_fields_memory_in_bytes": 32456,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 79565,
          "doc_values_memory_in_bytes": 210056,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 55,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 55,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 2248,
          "miss_count": 2997
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 542776,
          "deleted": 2234
        },
        "store": {
          "size_in_bytes": 399159007
        },
        "indexing": {
          "index_total": 2397610,
          "index_time_in_millis": 712309,
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
          "query_total": 18400,
          "query_time_in_millis": 18912,
          "query_current": 0,
          "fetch_total": 1420,
          "fetch_time_in_millis": 1386,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 9543,
          "total_time_in_millis": 2680129,
          "total_docs": 26945229,
          "total_size_in_bytes": 24052893782,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 258,
          "total_auto_throttle_in_bytes": 36396852
        },
        "refresh": {
          "total": 92964,
          "total_time_in_millis": 1574088,
          "listeners": 0
        },
        "flush": {
          "total": 6,
          "periodic": 4,
          "total_time_in_millis": 716
        },
        "warmer": {
          "current": 0,
          "total": 75677,
          "total_time_in_millis": 51171
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 75225,
          "hit_count": 3931,
          "miss_count": 71294,
          "cache_size": 0,
          "cache_count": 1917,
          "evictions": 1917
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 28,
          "memory_in_bytes": 862642,
          "terms_memory_in_bytes": 247608,
          "stored_fields_memory_in_bytes": 63616,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 161810,
          "doc_values_memory_in_bytes": 389608,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542672001228,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 110,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 4520,
          "miss_count": 5996
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 271388,
              "deleted": 1170
            },
            "store": {
              "size_in_bytes": 197803546
            },
            "indexing": {
              "index_total": 1198856,
              "index_time_in_millis": 363564,
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
              "query_total": 9195,
              "query_time_in_millis": 10196,
              "query_current": 0,
              "fetch_total": 710,
              "fetch_time_in_millis": 706,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 4778,
              "total_time_in_millis": 1397023,
              "total_docs": 13870956,
              "total_size_in_bytes": 12354236835,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 160,
              "total_auto_throttle_in_bytes": 17331834
            },
            "refresh": {
              "total": 46569,
              "total_time_in_millis": 800841,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 375
            },
            "warmer": {
              "current": 0,
              "total": 37925,
              "total_time_in_millis": 26469
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 32318,
              "hit_count": 1939,
              "miss_count": 30379,
              "cache_size": 0,
              "cache_count": 989,
              "evictions": 989
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 16,
              "memory_in_bytes": 449754,
              "terms_memory_in_bytes": 127677,
              "stored_fields_memory_in_bytes": 32456,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 79565,
              "doc_values_memory_in_bytes": 210056,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688489
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 2248,
              "miss_count": 2997
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOwqAQ==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "1198855",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "S1MOB1EWRbCytXU0toFmaQ",
                "history_uuid": "qacS1oHgTLuJxCWjI-6NDg",
                "sync_id": "iWqrAtKWTna58sc112nTbQ",
                "translog_generation": "20",
                "max_seq_no": "1198855"
              },
              "num_docs": 271388
            },
            "seq_no": {
              "max_seq_no": 1198855,
              "local_checkpoint": 1198855,
              "global_checkpoint": 1198855
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 271388,
              "deleted": 1064
            },
            "store": {
              "size_in_bytes": 201355461
            },
            "indexing": {
              "index_total": 1198754,
              "index_time_in_millis": 348745,
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
              "query_total": 9205,
              "query_time_in_millis": 8716,
              "query_current": 0,
              "fetch_total": 710,
              "fetch_time_in_millis": 680,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 4765,
              "total_time_in_millis": 1283106,
              "total_docs": 13074273,
              "total_size_in_bytes": 11698656947,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 98,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 46395,
              "total_time_in_millis": 773247,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 341
            },
            "warmer": {
              "current": 0,
              "total": 37752,
              "total_time_in_millis": 24702
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 42907,
              "hit_count": 1992,
              "miss_count": 40915,
              "cache_size": 0,
              "cache_count": 928,
              "evictions": 928
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 12,
              "memory_in_bytes": 412888,
              "terms_memory_in_bytes": 119931,
              "stored_fields_memory_in_bytes": 31160,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 82245,
              "doc_values_memory_in_bytes": 179552,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672001228,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688501
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 2272,
              "miss_count": 2999
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGK9kA==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "1198855",
                "max_unsafe_auto_id_timestamp": "1542672001228",
                "translog_uuid": "SvF9ln6zTuKijRor1q_-HQ",
                "history_uuid": "qacS1oHgTLuJxCWjI-6NDg",
                "sync_id": "iWqrAtKWTna58sc112nTbQ",
                "translog_generation": "20",
                "max_seq_no": "1198855"
              },
              "num_docs": 271388
            },
            "seq_no": {
              "max_seq_no": 1198855,
              "local_checkpoint": 1198855,
              "global_checkpoint": 1198855
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-es-6-2018.11.21": {
      "uuid": "_Pf-ul62RT-k_zPabX29vA",
      "primaries": {
        "docs": {
          "count": 297937,
          "deleted": 1166
        },
        "store": {
          "size_in_bytes": 218141175
        },
        "indexing": {
          "index_total": 1268379,
          "index_time_in_millis": 369494,
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
          "query_total": 5516,
          "query_time_in_millis": 10533,
          "query_current": 0,
          "fetch_total": 3199,
          "fetch_time_in_millis": 1943,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 4784,
          "total_time_in_millis": 1322426,
          "total_docs": 13747061,
          "total_size_in_bytes": 12127592588,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 52,
          "total_auto_throttle_in_bytes": 19065018
        },
        "refresh": {
          "total": 46648,
          "total_time_in_millis": 793273,
          "listeners": 0
        },
        "flush": {
          "total": 3,
          "periodic": 2,
          "total_time_in_millis": 450
        },
        "warmer": {
          "current": 0,
          "total": 38003,
          "total_time_in_millis": 25788
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 64668,
          "hit_count": 18505,
          "miss_count": 46163,
          "cache_size": 0,
          "cache_count": 742,
          "evictions": 742
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 15,
          "memory_in_bytes": 607307,
          "terms_memory_in_bytes": 137283,
          "stored_fields_memory_in_bytes": 32928,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 92444,
          "doc_values_memory_in_bytes": 344652,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 355603,
          "size_in_bytes": 343764755,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 55,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 43,
          "miss_count": 2262
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 595874,
          "deleted": 2332
        },
        "store": {
          "size_in_bytes": 435692695
        },
        "indexing": {
          "index_total": 2536624,
          "index_time_in_millis": 719109,
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
          "query_total": 11032,
          "query_time_in_millis": 20302,
          "query_current": 0,
          "fetch_total": 6415,
          "fetch_time_in_millis": 3638,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 9560,
          "total_time_in_millis": 2627451,
          "total_docs": 27458460,
          "total_size_in_bytes": 24232658893,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 145,
          "total_auto_throttle_in_bytes": 38130036
        },
        "refresh": {
          "total": 93116,
          "total_time_in_millis": 1553299,
          "listeners": 0
        },
        "flush": {
          "total": 6,
          "periodic": 4,
          "total_time_in_millis": 2932
        },
        "warmer": {
          "current": 0,
          "total": 75827,
          "total_time_in_millis": 51151
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 129858,
          "hit_count": 36307,
          "miss_count": 93551,
          "cache_size": 0,
          "cache_count": 1415,
          "evictions": 1415
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 31,
          "memory_in_bytes": 1137639,
          "terms_memory_in_bytes": 276419,
          "stored_fields_memory_in_bytes": 65968,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 184248,
          "doc_values_memory_in_bytes": 611004,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542758400795,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 711206,
          "size_in_bytes": 687529510,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 88,
          "miss_count": 4502
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 297937,
              "deleted": 1166
            },
            "store": {
              "size_in_bytes": 218141175
            },
            "indexing": {
              "index_total": 1268379,
              "index_time_in_millis": 369494,
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
              "query_total": 5516,
              "query_time_in_millis": 10533,
              "query_current": 0,
              "fetch_total": 3199,
              "fetch_time_in_millis": 1943,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 4784,
              "total_time_in_millis": 1322426,
              "total_docs": 13747061,
              "total_size_in_bytes": 12127592588,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 52,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 46648,
              "total_time_in_millis": 793273,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 450
            },
            "warmer": {
              "current": 0,
              "total": 38003,
              "total_time_in_millis": 25788
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 64668,
              "hit_count": 18505,
              "miss_count": 46163,
              "cache_size": 0,
              "cache_count": 742,
              "evictions": 742
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 15,
              "memory_in_bytes": 607307,
              "terms_memory_in_bytes": 137283,
              "stored_fields_memory_in_bytes": 32928,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 92444,
              "doc_values_memory_in_bytes": 344652,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 355603,
              "size_in_bytes": 343764755,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 43040711
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 43,
              "miss_count": 2262
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAY9Q==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "1268378",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "dLNA1yfKR8qMXEnXh9yYpw",
                "history_uuid": "Lz6eRoIsRBCLvIJauhG6bQ",
                "sync_id": "FI0QksOnQmS-MC627aJFkw",
                "translog_generation": "21",
                "max_seq_no": "1268378"
              },
              "num_docs": 297937
            },
            "seq_no": {
              "max_seq_no": 1268378,
              "local_checkpoint": 1268378,
              "global_checkpoint": 1268378
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 297937,
              "deleted": 1166
            },
            "store": {
              "size_in_bytes": 217551520
            },
            "indexing": {
              "index_total": 1268245,
              "index_time_in_millis": 349615,
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
              "query_total": 5516,
              "query_time_in_millis": 9769,
              "query_current": 0,
              "fetch_total": 3216,
              "fetch_time_in_millis": 1695,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 4776,
              "total_time_in_millis": 1305025,
              "total_docs": 13711399,
              "total_size_in_bytes": 12105066305,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 93,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 46468,
              "total_time_in_millis": 760026,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 2482
            },
            "warmer": {
              "current": 0,
              "total": 37824,
              "total_time_in_millis": 25363
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 65190,
              "hit_count": 17802,
              "miss_count": 47388,
              "cache_size": 0,
              "cache_count": 673,
              "evictions": 673
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 16,
              "memory_in_bytes": 530332,
              "terms_memory_in_bytes": 139136,
              "stored_fields_memory_in_bytes": 33040,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 91804,
              "doc_values_memory_in_bytes": 266352,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758400795,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 355603,
              "size_in_bytes": 343764755,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 43040546
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 45,
              "miss_count": 2240
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGZlgQ==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "1268378",
                "max_unsafe_auto_id_timestamp": "1542758400795",
                "translog_uuid": "CrXOjRDkQgmWHXa2LLkzbQ",
                "history_uuid": "Lz6eRoIsRBCLvIJauhG6bQ",
                "sync_id": "FI0QksOnQmS-MC627aJFkw",
                "translog_generation": "21",
                "max_seq_no": "1268378"
              },
              "num_docs": 297937
            },
            "seq_no": {
              "max_seq_no": 1268378,
              "local_checkpoint": 1268378,
              "global_checkpoint": 1268378
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-es-6-2018.11.22": {
      "uuid": "1w8VYA0VQb2KPqbBpYx6Hw",
      "primaries": {
        "docs": {
          "count": 83362,
          "deleted": 520
        },
        "store": {
          "size_in_bytes": 59201373
        },
        "indexing": {
          "index_total": 377020,
          "index_time_in_millis": 101176,
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
          "query_total": 13,
          "query_time_in_millis": 29,
          "query_current": 0,
          "fetch_total": 1,
          "fetch_time_in_millis": 1,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 1255,
          "total_time_in_millis": 474721,
          "total_docs": 5356491,
          "total_size_in_bytes": 4370296631,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 113,
          "total_auto_throttle_in_bytes": 19065018
        },
        "refresh": {
          "total": 12280,
          "total_time_in_millis": 204942,
          "listeners": 0
        },
        "flush": {
          "total": 0,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 10020,
          "total_time_in_millis": 6244
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 6,
          "hit_count": 0,
          "miss_count": 6,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 9,
          "memory_in_bytes": 202019,
          "terms_memory_in_bytes": 56736,
          "stored_fields_memory_in_bytes": 11264,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 25399,
          "doc_values_memory_in_bytes": 108620,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 10896,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 377020,
          "size_in_bytes": 353715050,
          "uncommitted_operations": 377020,
          "uncommitted_size_in_bytes": 353715050,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 166692,
          "deleted": 910
        },
        "store": {
          "size_in_bytes": 120951498
        },
        "indexing": {
          "index_total": 470083,
          "index_time_in_millis": 124010,
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
          "query_total": 18,
          "query_time_in_millis": 29,
          "query_current": 0,
          "fetch_total": 1,
          "fetch_time_in_millis": 1,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 1567,
          "total_time_in_millis": 535829,
          "total_docs": 6165445,
          "total_size_in_bytes": 4980564223,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 113,
          "total_auto_throttle_in_bytes": 40036538
        },
        "refresh": {
          "total": 15314,
          "total_time_in_millis": 251343,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 1,
          "total_time_in_millis": 165
        },
        "warmer": {
          "current": 0,
          "total": 12494,
          "total_time_in_millis": 7824
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 6,
          "hit_count": 0,
          "miss_count": 6,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 18,
          "memory_in_bytes": 441816,
          "terms_memory_in_bytes": 116147,
          "stored_fields_memory_in_bytes": 22208,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 50853,
          "doc_values_memory_in_bytes": 252608,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 21768,
          "max_unsafe_auto_id_timestamp": 1542861738182,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 966073,
          "size_in_bytes": 906641217,
          "uncommitted_operations": 466290,
          "uncommitted_size_in_bytes": 436992414,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 83362,
              "deleted": 520
            },
            "store": {
              "size_in_bytes": 59201373
            },
            "indexing": {
              "index_total": 377020,
              "index_time_in_millis": 101176,
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
              "query_total": 13,
              "query_time_in_millis": 29,
              "query_current": 0,
              "fetch_total": 1,
              "fetch_time_in_millis": 1,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 1255,
              "total_time_in_millis": 474721,
              "total_docs": 5356491,
              "total_size_in_bytes": 4370296631,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 113,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 12280,
              "total_time_in_millis": 204942,
              "listeners": 0
            },
            "flush": {
              "total": 0,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 10020,
              "total_time_in_millis": 6244
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6,
              "hit_count": 0,
              "miss_count": 6,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 9,
              "memory_in_bytes": 202019,
              "terms_memory_in_bytes": 56736,
              "stored_fields_memory_in_bytes": 11264,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 25399,
              "doc_values_memory_in_bytes": 108620,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 10896,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 377020,
              "size_in_bytes": 353715050,
              "uncommitted_operations": 377020,
              "uncommitted_size_in_bytes": 353715050,
              "earliest_last_modified_age": 22586736
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAV3g==",
              "generation": 2,
              "user_data": {
                "local_checkpoint": "-1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "6j4hzz7kRH-B6oVmDviYIQ",
                "history_uuid": "-S_W9SkLROKK-y5e7OSWSA",
                "translog_generation": "1",
                "max_seq_no": "-1"
              },
              "num_docs": 0
            },
            "seq_no": {
              "max_seq_no": 377019,
              "local_checkpoint": 377019,
              "global_checkpoint": 287755
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 83330,
              "deleted": 390
            },
            "store": {
              "size_in_bytes": 61750125
            },
            "indexing": {
              "index_total": 93063,
              "index_time_in_millis": 22834,
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
              "query_total": 5,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 312,
              "total_time_in_millis": 61108,
              "total_docs": 808954,
              "total_size_in_bytes": 610267592,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3034,
              "total_time_in_millis": 46401,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 1,
              "total_time_in_millis": 165
            },
            "warmer": {
              "current": 0,
              "total": 2474,
              "total_time_in_millis": 1580
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 9,
              "memory_in_bytes": 239797,
              "terms_memory_in_bytes": 59411,
              "stored_fields_memory_in_bytes": 10944,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 25454,
              "doc_values_memory_in_bytes": 143988,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 10872,
              "max_unsafe_auto_id_timestamp": 1542861738182,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 589053,
              "size_in_bytes": 552926167,
              "uncommitted_operations": 89270,
              "uncommitted_size_in_bytes": 83277364,
              "earliest_last_modified_age": 14206028
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGcV5A==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "287587",
                "max_unsafe_auto_id_timestamp": "1542861738182",
                "translog_uuid": "pNA-nesWTt28sI9NVP0izQ",
                "history_uuid": "-S_W9SkLROKK-y5e7OSWSA",
                "translog_generation": "12",
                "max_seq_no": "287587"
              },
              "num_docs": 63870
            },
            "seq_no": {
              "max_seq_no": 377019,
              "local_checkpoint": 287755,
              "global_checkpoint": 287755
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-beats-6-2018.11.19": {
      "uuid": "PwSX9DNHR8WyOP2JXzC9vQ",
      "primaries": {
        "docs": {
          "count": 33339,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 20884310
        },
        "indexing": {
          "index_total": 25477,
          "index_time_in_millis": 39834,
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
          "query_total": 1300,
          "query_time_in_millis": 2668,
          "query_current": 0,
          "fetch_total": 1088,
          "fetch_time_in_millis": 59,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 1209,
          "total_time_in_millis": 298693,
          "total_docs": 5802420,
          "total_size_in_bytes": 4158152520,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 11269,
          "total_time_in_millis": 191789,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 20
        },
        "warmer": {
          "current": 0,
          "total": 11266,
          "total_time_in_millis": 713
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 2527,
          "hit_count": 837,
          "miss_count": 1690,
          "cache_size": 0,
          "cache_count": 5,
          "evictions": 5
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 3,
          "memory_in_bytes": 70822,
          "terms_memory_in_bytes": 26211,
          "stored_fields_memory_in_bytes": 3048,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 8799,
          "doc_values_memory_in_bytes": 32764,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542632113777,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 55,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 55,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 105,
          "miss_count": 749
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 62
        }
      },
      "total": {
        "docs": {
          "count": 66678,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 41901746
        },
        "indexing": {
          "index_total": 50677,
          "index_time_in_millis": 86485,
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
          "query_total": 2599,
          "query_time_in_millis": 5472,
          "query_current": 0,
          "fetch_total": 2177,
          "fetch_time_in_millis": 94,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 2415,
          "total_time_in_millis": 606552,
          "total_docs": 11648090,
          "total_size_in_bytes": 8339286859,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 22526,
          "total_time_in_millis": 390767,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 54
        },
        "warmer": {
          "current": 0,
          "total": 22521,
          "total_time_in_millis": 1334
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 5141,
          "hit_count": 1765,
          "miss_count": 3376,
          "cache_size": 0,
          "cache_count": 8,
          "evictions": 8
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 13,
          "memory_in_bytes": 167620,
          "terms_memory_in_bytes": 79987,
          "stored_fields_memory_in_bytes": 8272,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 18285,
          "doc_values_memory_in_bytes": 61076,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542632843798,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 110,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 203,
          "miss_count": 1514
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 74
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 33339,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 21017436
            },
            "indexing": {
              "index_total": 25200,
              "index_time_in_millis": 46651,
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
              "query_total": 1299,
              "query_time_in_millis": 2804,
              "query_current": 0,
              "fetch_total": 1089,
              "fetch_time_in_millis": 35,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 1206,
              "total_time_in_millis": 307859,
              "total_docs": 5845670,
              "total_size_in_bytes": 4181134339,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 11257,
              "total_time_in_millis": 198978,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 34
            },
            "warmer": {
              "current": 0,
              "total": 11255,
              "total_time_in_millis": 621
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 2614,
              "hit_count": 928,
              "miss_count": 1686,
              "cache_size": 0,
              "cache_count": 3,
              "evictions": 3
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 10,
              "memory_in_bytes": 96798,
              "terms_memory_in_bytes": 53776,
              "stored_fields_memory_in_bytes": 5224,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 9486,
              "doc_values_memory_in_bytes": 28312,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632843798,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195095112
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 98,
              "miss_count": 765
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 11
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBh6jQ==",
              "generation": 9,
              "user_data": {
                "local_checkpoint": "33338",
                "max_unsafe_auto_id_timestamp": "1542632843798",
                "translog_uuid": "NsjZiyzNR4WRS_xGKe0t3g",
                "history_uuid": "_blqyi2YQji6u7y6uBnfTQ",
                "sync_id": "A58hYVPYSWu83VZ9P0PpxQ",
                "translog_generation": "3",
                "max_seq_no": "33338"
              },
              "num_docs": 33339
            },
            "seq_no": {
              "max_seq_no": 33338,
              "local_checkpoint": 33338,
              "global_checkpoint": 33338
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 33339,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 20884310
            },
            "indexing": {
              "index_total": 25477,
              "index_time_in_millis": 39834,
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
              "query_total": 1300,
              "query_time_in_millis": 2668,
              "query_current": 0,
              "fetch_total": 1088,
              "fetch_time_in_millis": 59,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 1209,
              "total_time_in_millis": 298693,
              "total_docs": 5802420,
              "total_size_in_bytes": 4158152520,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 11269,
              "total_time_in_millis": 191789,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 20
            },
            "warmer": {
              "current": 0,
              "total": 11266,
              "total_time_in_millis": 713
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 2527,
              "hit_count": 837,
              "miss_count": 1690,
              "cache_size": 0,
              "cache_count": 5,
              "evictions": 5
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 3,
              "memory_in_bytes": 70822,
              "terms_memory_in_bytes": 26211,
              "stored_fields_memory_in_bytes": 3048,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 8799,
              "doc_values_memory_in_bytes": 32764,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632113777,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195095130
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 105,
              "miss_count": 749
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 62
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWF7MZQ==",
              "generation": 8,
              "user_data": {
                "local_checkpoint": "33338",
                "max_unsafe_auto_id_timestamp": "1542632113777",
                "translog_uuid": "XGI13bs6T8eqzTd0ToIMRQ",
                "history_uuid": "_blqyi2YQji6u7y6uBnfTQ",
                "sync_id": "A58hYVPYSWu83VZ9P0PpxQ",
                "translog_generation": "9",
                "max_seq_no": "33338"
              },
              "num_docs": 33339
            },
            "seq_no": {
              "max_seq_no": 33338,
              "local_checkpoint": 33338,
              "global_checkpoint": 33338
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-es-6-2018.11.17": {
      "uuid": "2qIwkg92Sb2b1VKCIzvy8A",
      "primaries": {
        "docs": {
          "count": 182762,
          "deleted": 364
        },
        "store": {
          "size_in_bytes": 128193819
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 9577,
          "query_time_in_millis": 1408,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 3,
          "total_time_in_millis": 3,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 1,
          "total_time_in_millis": 30
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 24271,
          "hit_count": 1402,
          "miss_count": 22869,
          "cache_size": 0,
          "cache_count": 5,
          "evictions": 5
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 9,
          "memory_in_bytes": 296681,
          "terms_memory_in_bytes": 91617,
          "stored_fields_memory_in_bytes": 22328,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 54076,
          "doc_values_memory_in_bytes": 128660,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542438741718,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 110,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 5203,
          "miss_count": 83
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 561
        }
      },
      "total": {
        "docs": {
          "count": 365524,
          "deleted": 728
        },
        "store": {
          "size_in_bytes": 256387638
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 19163,
          "query_time_in_millis": 2967,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 6,
          "total_time_in_millis": 3,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 2,
          "total_time_in_millis": 45
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 48182,
          "hit_count": 2657,
          "miss_count": 45525,
          "cache_size": 0,
          "cache_count": 10,
          "evictions": 10
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 18,
          "memory_in_bytes": 593362,
          "terms_memory_in_bytes": 183234,
          "stored_fields_memory_in_bytes": 44656,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 108152,
          "doc_values_memory_in_bytes": 257320,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542438741718,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 220,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 220,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 10365,
          "miss_count": 167
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 1092
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 182762,
              "deleted": 364
            },
            "store": {
              "size_in_bytes": 128193819
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 9577,
              "query_time_in_millis": 1408,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 3,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 30
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 24271,
              "hit_count": 1402,
              "miss_count": 22869,
              "cache_size": 0,
              "cache_count": 5,
              "evictions": 5
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 9,
              "memory_in_bytes": 296681,
              "terms_memory_in_bytes": 91617,
              "stored_fields_memory_in_bytes": 22328,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 54076,
              "doc_values_memory_in_bytes": 128660,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542438741718,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 110,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 110,
              "earliest_last_modified_age": 234479336
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5203,
              "miss_count": 83
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 561
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbObglw==",
              "generation": 10,
              "user_data": {
                "local_checkpoint": "629701",
                "max_unsafe_auto_id_timestamp": "1542438741718",
                "translog_uuid": "xyMCj0rPRmaE2P9xg7VHzg",
                "history_uuid": "4vQCVzKsS72zSsZANzMOXA",
                "sync_id": "s-cf1fyUSZWCVKCBz5pbdQ",
                "translog_generation": "1",
                "max_seq_no": "629701"
              },
              "num_docs": 182762
            },
            "seq_no": {
              "max_seq_no": 629701,
              "local_checkpoint": 629701,
              "global_checkpoint": 629701
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 182762,
              "deleted": 364
            },
            "store": {
              "size_in_bytes": 128193819
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 9586,
              "query_time_in_millis": 1559,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 0,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 15
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 23911,
              "hit_count": 1255,
              "miss_count": 22656,
              "cache_size": 0,
              "cache_count": 5,
              "evictions": 5
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 9,
              "memory_in_bytes": 296681,
              "terms_memory_in_bytes": 91617,
              "stored_fields_memory_in_bytes": 22328,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 54076,
              "doc_values_memory_in_bytes": 128660,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542438741718,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 110,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 110,
              "earliest_last_modified_age": 234545447
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5162,
              "miss_count": 84
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 530
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4Arggbw==",
              "generation": 10,
              "user_data": {
                "local_checkpoint": "629701",
                "max_unsafe_auto_id_timestamp": "1542438741718",
                "translog_uuid": "Ut9NB69hR8i8k8LsfvkLnA",
                "history_uuid": "4vQCVzKsS72zSsZANzMOXA",
                "sync_id": "s-cf1fyUSZWCVKCBz5pbdQ",
                "translog_generation": "1",
                "max_seq_no": "629701"
              },
              "num_docs": 182762
            },
            "seq_no": {
              "max_seq_no": 629701,
              "local_checkpoint": 629701,
              "global_checkpoint": 629701
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-es-6-2018.11.18": {
      "uuid": "D3Hq7e7UQnm6MBAsjq_AiQ",
      "primaries": {
        "docs": {
          "count": 198776,
          "deleted": 392
        },
        "store": {
          "size_in_bytes": 136279158
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 9583,
          "query_time_in_millis": 1409,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 3,
          "total_time_in_millis": 0,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 1
        },
        "warmer": {
          "current": 0,
          "total": 1,
          "total_time_in_millis": 82
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 28157,
          "hit_count": 1488,
          "miss_count": 26669,
          "cache_size": 0,
          "cache_count": 12,
          "evictions": 12
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 8,
          "memory_in_bytes": 341514,
          "terms_memory_in_bytes": 85501,
          "stored_fields_memory_in_bytes": 23264,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 57101,
          "doc_values_memory_in_bytes": 175648,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542499200440,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 275,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 275,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 5190,
          "miss_count": 83
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 397552,
          "deleted": 784
        },
        "store": {
          "size_in_bytes": 272558317
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 19163,
          "query_time_in_millis": 3128,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 6,
          "total_time_in_millis": 2,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 1
        },
        "warmer": {
          "current": 0,
          "total": 2,
          "total_time_in_millis": 105
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 55999,
          "hit_count": 2962,
          "miss_count": 53037,
          "cache_size": 0,
          "cache_count": 18,
          "evictions": 18
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 16,
          "memory_in_bytes": 683028,
          "terms_memory_in_bytes": 171002,
          "stored_fields_memory_in_bytes": 46528,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 114202,
          "doc_values_memory_in_bytes": 351296,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542499200440,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 550,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 550,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 10365,
          "miss_count": 167
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 198776,
              "deleted": 392
            },
            "store": {
              "size_in_bytes": 136279159
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 9580,
              "query_time_in_millis": 1719,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 2,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 23
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 27842,
              "hit_count": 1474,
              "miss_count": 26368,
              "cache_size": 0,
              "cache_count": 6,
              "evictions": 6
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 8,
              "memory_in_bytes": 341514,
              "terms_memory_in_bytes": 85501,
              "stored_fields_memory_in_bytes": 23264,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 57101,
              "doc_values_memory_in_bytes": 175648,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542499200440,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 275,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 275,
              "earliest_last_modified_age": 281492162
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5175,
              "miss_count": 84
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "XhXQZCLuqrD7+aLbMA3YPg==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "682559",
                "max_unsafe_auto_id_timestamp": "1542499200440",
                "translog_uuid": "cCSmreNvRP-f9ix0VUffjA",
                "history_uuid": "YU-151QoQsa1uXO5NjmeIA",
                "sync_id": "9pWudEf2SnqBhCppevgvJw",
                "translog_generation": "13",
                "max_seq_no": "682559"
              },
              "num_docs": 198776
            },
            "seq_no": {
              "max_seq_no": 682559,
              "local_checkpoint": 682559,
              "global_checkpoint": 682559
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 198776,
              "deleted": 392
            },
            "store": {
              "size_in_bytes": 136279158
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 9583,
              "query_time_in_millis": 1409,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 0,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 1
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 82
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 28157,
              "hit_count": 1488,
              "miss_count": 26669,
              "cache_size": 0,
              "cache_count": 12,
              "evictions": 12
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 8,
              "memory_in_bytes": 341514,
              "terms_memory_in_bytes": 85501,
              "stored_fields_memory_in_bytes": 23264,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 57101,
              "doc_values_memory_in_bytes": 175648,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542499200440,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 275,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 275,
              "earliest_last_modified_age": 235814815
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5190,
              "miss_count": 83
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "ehuu6qAbGslqqS83pWAC0Q==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "682559",
                "max_unsafe_auto_id_timestamp": "1542499200440",
                "translog_uuid": "qe97UBN7Shap4mOOprIgmA",
                "history_uuid": "YU-151QoQsa1uXO5NjmeIA",
                "sync_id": "9pWudEf2SnqBhCppevgvJw",
                "translog_generation": "1",
                "max_seq_no": "682559"
              },
              "num_docs": 198776
            },
            "seq_no": {
              "max_seq_no": 682559,
              "local_checkpoint": 682559,
              "global_checkpoint": 682559
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    "uuid2-6.5.0-2018.11.20": {
      "uuid": "dWmIYY2BQcOuIE4vw_SbZg",
      "primaries": {
        "docs": {
          "count": 3110399502,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 1495270214916
        },
        "indexing": {
          "index_total": 3110399502,
          "index_time_in_millis": 626702376,
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
          "query_total": 72548,
          "query_time_in_millis": 16912726,
          "query_current": 0,
          "fetch_total": 338,
          "fetch_time_in_millis": 14482,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 53882,
          "total_time_in_millis": 1686509053,
          "total_docs": 9397853396,
          "total_size_in_bytes": 5437468006019,
          "total_stopped_time_in_millis": 196815,
          "total_throttled_time_in_millis": 1305875200,
          "total_auto_throttle_in_bytes": 86459857
        },
        "refresh": {
          "total": 202444,
          "total_time_in_millis": 109809304,
          "listeners": 0
        },
        "flush": {
          "total": 7495,
          "periodic": 7479,
          "total_time_in_millis": 7833089
        },
        "warmer": {
          "current": 0,
          "total": 194820,
          "total_time_in_millis": 11185
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 108103,
          "hit_count": 51646,
          "miss_count": 56457,
          "cache_size": 0,
          "cache_count": 1193,
          "evictions": 1193
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 768,
          "memory_in_bytes": 3271053145,
          "terms_memory_in_bytes": 2603600704,
          "stored_fields_memory_in_bytes": 598647984,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 68624473,
          "doc_values_memory_in_bytes": 179984,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542672002521,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 880,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 880,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 3110399502,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 1495270214916
        },
        "indexing": {
          "index_total": 3110399502,
          "index_time_in_millis": 626702376,
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
          "query_total": 72548,
          "query_time_in_millis": 16912726,
          "query_current": 0,
          "fetch_total": 338,
          "fetch_time_in_millis": 14482,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 53882,
          "total_time_in_millis": 1686509053,
          "total_docs": 9397853396,
          "total_size_in_bytes": 5437468006019,
          "total_stopped_time_in_millis": 196815,
          "total_throttled_time_in_millis": 1305875200,
          "total_auto_throttle_in_bytes": 86459857
        },
        "refresh": {
          "total": 202444,
          "total_time_in_millis": 109809304,
          "listeners": 0
        },
        "flush": {
          "total": 7495,
          "periodic": 7479,
          "total_time_in_millis": 7833089
        },
        "warmer": {
          "current": 0,
          "total": 194820,
          "total_time_in_millis": 11185
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 108103,
          "hit_count": 51646,
          "miss_count": 56457,
          "cache_size": 0,
          "cache_count": 1193,
          "evictions": 1193
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 768,
          "memory_in_bytes": 3271053145,
          "terms_memory_in_bytes": 2603600704,
          "stored_fields_memory_in_bytes": 598647984,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 68624473,
          "doc_values_memory_in_bytes": 179984,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542672002521,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 880,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 880,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 194376557,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93868380151
            },
            "indexing": {
              "index_total": 194376557,
              "index_time_in_millis": 39281673,
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
              "query_total": 4538,
              "query_time_in_millis": 1050911,
              "query_current": 0,
              "fetch_total": 172,
              "fetch_time_in_millis": 2791,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3535,
              "total_time_in_millis": 103850326,
              "total_docs": 586985905,
              "total_size_in_bytes": 340300697585,
              "total_stopped_time_in_millis": 8656,
              "total_throttled_time_in_millis": 80681154,
              "total_auto_throttle_in_bytes": 6291456
            },
            "refresh": {
              "total": 12409,
              "total_time_in_millis": 6956997,
              "listeners": 0
            },
            "flush": {
              "total": 468,
              "periodic": 467,
              "total_time_in_millis": 531814
            },
            "warmer": {
              "current": 0,
              "total": 11936,
              "total_time_in_millis": 683
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 7068,
              "hit_count": 3298,
              "miss_count": 3770,
              "cache_size": 0,
              "cache_count": 83,
              "evictions": 83
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 51,
              "memory_in_bytes": 213680177,
              "terms_memory_in_bytes": 171805713,
              "stored_fields_memory_in_bytes": 37568192,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4295860,
              "doc_values_memory_in_bytes": 10412,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108686442
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AryL4g==",
              "generation": 471,
              "user_data": {
                "local_checkpoint": "194376556",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "YllyY3V8TpitCx833p5WIw",
                "history_uuid": "rmw99-TITgSpXWcNo7NNNA",
                "sync_id": "zknkOjhMTQ62LCOFqscnpA",
                "translog_generation": "3712",
                "max_seq_no": "194376556"
              },
              "num_docs": 194376557
            },
            "seq_no": {
              "max_seq_no": 194376556,
              "local_checkpoint": 194376556,
              "global_checkpoint": 194376556
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "1": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 194404184,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93945124930
            },
            "indexing": {
              "index_total": 194404184,
              "index_time_in_millis": 38967067,
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
              "query_total": 4538,
              "query_time_in_millis": 1202478,
              "query_current": 0,
              "fetch_total": 15,
              "fetch_time_in_millis": 964,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3681,
              "total_time_in_millis": 104508219,
              "total_docs": 590175166,
              "total_size_in_bytes": 342679922433,
              "total_stopped_time_in_millis": 12537,
              "total_throttled_time_in_millis": 80633374,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12986,
              "total_time_in_millis": 6186145,
              "listeners": 0
            },
            "flush": {
              "total": 467,
              "periodic": 466,
              "total_time_in_millis": 439532
            },
            "warmer": {
              "current": 0,
              "total": 12510,
              "total_time_in_millis": 619
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 7435,
              "hit_count": 3571,
              "miss_count": 3864,
              "cache_size": 0,
              "cache_count": 87,
              "evictions": 87
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 49,
              "memory_in_bytes": 211874629,
              "terms_memory_in_bytes": 169867287,
              "stored_fields_memory_in_bytes": 37696232,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4295434,
              "doc_values_memory_in_bytes": 15676,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688639
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGLIUQ==",
              "generation": 471,
              "user_data": {
                "local_checkpoint": "194404183",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "KfB9tYPlR7CiZmx4CWPVVA",
                "history_uuid": "EhWfwcSASBqi1XnqZtKZWw",
                "sync_id": "rl3Fp49OQ2GnwaVGTVIKog",
                "translog_generation": "3707",
                "max_seq_no": "194404183"
              },
              "num_docs": 194404184
            },
            "seq_no": {
              "max_seq_no": 194404183,
              "local_checkpoint": 194404183,
              "global_checkpoint": 194404183
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "2": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 194411366,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93750686895
            },
            "indexing": {
              "index_total": 194411366,
              "index_time_in_millis": 38067573,
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
              "query_total": 4523,
              "query_time_in_millis": 1084909,
              "query_current": 0,
              "fetch_total": 11,
              "fetch_time_in_millis": 1167,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3382,
              "total_time_in_millis": 103954890,
              "total_docs": 581657976,
              "total_size_in_bytes": 336508806698,
              "total_stopped_time_in_millis": 656,
              "total_throttled_time_in_millis": 79902691,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12865,
              "total_time_in_millis": 6699657,
              "listeners": 0
            },
            "flush": {
              "total": 467,
              "periodic": 466,
              "total_time_in_millis": 468597
            },
            "warmer": {
              "current": 0,
              "total": 12395,
              "total_time_in_millis": 689
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6604,
              "hit_count": 3168,
              "miss_count": 3436,
              "cache_size": 0,
              "cache_count": 78,
              "evictions": 78
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 51,
              "memory_in_bytes": 217947348,
              "terms_memory_in_bytes": 176409672,
              "stored_fields_memory_in_bytes": 37232264,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4289448,
              "doc_values_memory_in_bytes": 15964,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688469
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOwp/g==",
              "generation": 470,
              "user_data": {
                "local_checkpoint": "194411365",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "GbzTkFM-QM--p1VQHv7c3Q",
                "history_uuid": "HSm_K7SRQbGhSZ3ZY6_vww",
                "sync_id": "yFkL4ttpT5yrHfcvwzxQ4A",
                "translog_generation": "3704",
                "max_seq_no": "194411365"
              },
              "num_docs": 194411366
            },
            "seq_no": {
              "max_seq_no": 194411365,
              "local_checkpoint": 194411365,
              "global_checkpoint": 194411365
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "3": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 194379067,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93053836465
            },
            "indexing": {
              "index_total": 194379067,
              "index_time_in_millis": 39296303,
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
              "query_total": 4538,
              "query_time_in_millis": 962267,
              "query_current": 0,
              "fetch_total": 7,
              "fetch_time_in_millis": 341,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3297,
              "total_time_in_millis": 106207199,
              "total_docs": 589878502,
              "total_size_in_bytes": 340598382180,
              "total_stopped_time_in_millis": 19924,
              "total_throttled_time_in_millis": 81783413,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12391,
              "total_time_in_millis": 7367246,
              "listeners": 0
            },
            "flush": {
              "total": 470,
              "periodic": 469,
              "total_time_in_millis": 493300
            },
            "warmer": {
              "current": 0,
              "total": 11913,
              "total_time_in_millis": 693
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6671,
              "hit_count": 3168,
              "miss_count": 3503,
              "cache_size": 0,
              "cache_count": 76,
              "evictions": 76
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 46,
              "memory_in_bytes": 196097367,
              "terms_memory_in_bytes": 154601686,
              "stored_fields_memory_in_bytes": 37201936,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4284657,
              "doc_values_memory_in_bytes": 9088,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108687414
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBuy+w==",
              "generation": 474,
              "user_data": {
                "local_checkpoint": "194379066",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "fYIc4pMrSDuMl2Fd7wZp6g",
                "history_uuid": "ZB5HA7WFSqWeaAOrVbUeGA",
                "sync_id": "AeB4n0jFSFSajmU6fdcBbw",
                "translog_generation": "3712",
                "max_seq_no": "194379066"
              },
              "num_docs": 194379067
            },
            "seq_no": {
              "max_seq_no": 194379066,
              "local_checkpoint": 194379066,
              "global_checkpoint": 194379066
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "4": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 194415187,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93026411040
            },
            "indexing": {
              "index_total": 194415187,
              "index_time_in_millis": 37376249,
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
              "query_total": 4538,
              "query_time_in_millis": 1040443,
              "query_current": 0,
              "fetch_total": 9,
              "fetch_time_in_millis": 501,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3261,
              "total_time_in_millis": 106702087,
              "total_docs": 589074436,
              "total_size_in_bytes": 339832803131,
              "total_stopped_time_in_millis": 2,
              "total_throttled_time_in_millis": 83656172,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12396,
              "total_time_in_millis": 7380839,
              "listeners": 0
            },
            "flush": {
              "total": 468,
              "periodic": 467,
              "total_time_in_millis": 542848
            },
            "warmer": {
              "current": 0,
              "total": 11921,
              "total_time_in_millis": 704
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6487,
              "hit_count": 3179,
              "miss_count": 3308,
              "cache_size": 0,
              "cache_count": 73,
              "evictions": 73
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 47,
              "memory_in_bytes": 195948847,
              "terms_memory_in_bytes": 154551910,
              "stored_fields_memory_in_bytes": 37098880,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4286165,
              "doc_values_memory_in_bytes": 11892,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108686439
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AryXUA==",
              "generation": 472,
              "user_data": {
                "local_checkpoint": "194415186",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "zcSm17bLSXioH2ttvzx3Vg",
                "history_uuid": "WoxQ6YkfToaf3lm0p_WG1A",
                "sync_id": "U49cyAolQxOue-jYMuNFLg",
                "translog_generation": "3715",
                "max_seq_no": "194415186"
              },
              "num_docs": 194415187
            },
            "seq_no": {
              "max_seq_no": 194415186,
              "local_checkpoint": 194415186,
              "global_checkpoint": 194415186
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "5": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 194395237,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93136452568
            },
            "indexing": {
              "index_total": 194395237,
              "index_time_in_millis": 37192317,
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
              "query_total": 4538,
              "query_time_in_millis": 1178967,
              "query_current": 0,
              "fetch_total": 11,
              "fetch_time_in_millis": 844,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3386,
              "total_time_in_millis": 104430188,
              "total_docs": 590175532,
              "total_size_in_bytes": 341001079067,
              "total_stopped_time_in_millis": 12788,
              "total_throttled_time_in_millis": 81017628,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12966,
              "total_time_in_millis": 6607214,
              "listeners": 0
            },
            "flush": {
              "total": 469,
              "periodic": 468,
              "total_time_in_millis": 446309
            },
            "warmer": {
              "current": 0,
              "total": 12488,
              "total_time_in_millis": 718
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6703,
              "hit_count": 3155,
              "miss_count": 3548,
              "cache_size": 0,
              "cache_count": 69,
              "evictions": 69
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 47,
              "memory_in_bytes": 199586585,
              "terms_memory_in_bytes": 158097933,
              "stored_fields_memory_in_bytes": 37186216,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4284424,
              "doc_values_memory_in_bytes": 18012,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688652
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGK9jg==",
              "generation": 472,
              "user_data": {
                "local_checkpoint": "194395236",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "7guYn0fMQ1GFcJU-vPR6zA",
                "history_uuid": "dWNvY5bhT66e1BZjki5psA",
                "sync_id": "bFOldtHIQ8Ozpzx4vF91_w",
                "translog_generation": "3711",
                "max_seq_no": "194395236"
              },
              "num_docs": 194395237
            },
            "seq_no": {
              "max_seq_no": 194395236,
              "local_checkpoint": 194395236,
              "global_checkpoint": 194395236
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "6": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 194381152,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93236163670
            },
            "indexing": {
              "index_total": 194381152,
              "index_time_in_millis": 39212626,
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
              "query_total": 4523,
              "query_time_in_millis": 1069386,
              "query_current": 0,
              "fetch_total": 9,
              "fetch_time_in_millis": 1155,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3235,
              "total_time_in_millis": 106279461,
              "total_docs": 586822681,
              "total_size_in_bytes": 339150759470,
              "total_stopped_time_in_millis": 5798,
              "total_throttled_time_in_millis": 82368233,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12840,
              "total_time_in_millis": 6731260,
              "listeners": 0
            },
            "flush": {
              "total": 469,
              "periodic": 468,
              "total_time_in_millis": 461036
            },
            "warmer": {
              "current": 0,
              "total": 12364,
              "total_time_in_millis": 660
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6414,
              "hit_count": 3167,
              "miss_count": 3247,
              "cache_size": 0,
              "cache_count": 77,
              "evictions": 77
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 53,
              "memory_in_bytes": 198477554,
              "terms_memory_in_bytes": 156760889,
              "stored_fields_memory_in_bytes": 37424128,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4284357,
              "doc_values_memory_in_bytes": 8180,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688400
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOwqAg==",
              "generation": 472,
              "user_data": {
                "local_checkpoint": "194381151",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "aU_2CmlzQFq1agI4B2SLQA",
                "history_uuid": "FdulhOqjREWcuIF9xBm5zA",
                "sync_id": "4BDkwBxGQvOl8uWuZd_b7Q",
                "translog_generation": "3709",
                "max_seq_no": "194381151"
              },
              "num_docs": 194381152
            },
            "seq_no": {
              "max_seq_no": 194381151,
              "local_checkpoint": 194381151,
              "global_checkpoint": 194381151
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "7": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 194384554,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93217705130
            },
            "indexing": {
              "index_total": 194384554,
              "index_time_in_millis": 40681505,
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
              "query_total": 4538,
              "query_time_in_millis": 960626,
              "query_current": 0,
              "fetch_total": 8,
              "fetch_time_in_millis": 490,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3171,
              "total_time_in_millis": 106513687,
              "total_docs": 585750583,
              "total_size_in_bytes": 338380493639,
              "total_stopped_time_in_millis": 18284,
              "total_throttled_time_in_millis": 82441537,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12372,
              "total_time_in_millis": 7343661,
              "listeners": 0
            },
            "flush": {
              "total": 470,
              "periodic": 469,
              "total_time_in_millis": 511478
            },
            "warmer": {
              "current": 0,
              "total": 11891,
              "total_time_in_millis": 680
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6377,
              "hit_count": 3028,
              "miss_count": 3349,
              "cache_size": 0,
              "cache_count": 67,
              "evictions": 67
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 45,
              "memory_in_bytes": 200446250,
              "terms_memory_in_bytes": 158749560,
              "stored_fields_memory_in_bytes": 37401912,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4287638,
              "doc_values_memory_in_bytes": 7140,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108687417
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBur4g==",
              "generation": 473,
              "user_data": {
                "local_checkpoint": "194384553",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "AsGZ8Q7AQhWv-9D_CTo71Q",
                "history_uuid": "A44gMwJCTYCPFeK5pbi24g",
                "sync_id": "8DEjpKMsTE-Gm0YuknXQWA",
                "translog_generation": "3722",
                "max_seq_no": "194384553"
              },
              "num_docs": 194384554
            },
            "seq_no": {
              "max_seq_no": 194384553,
              "local_checkpoint": 194384553,
              "global_checkpoint": 194384553
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "8": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 194411533,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93267437534
            },
            "indexing": {
              "index_total": 194411533,
              "index_time_in_millis": 38209697,
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
              "query_total": 4538,
              "query_time_in_millis": 1039058,
              "query_current": 0,
              "fetch_total": 8,
              "fetch_time_in_millis": 646,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3138,
              "total_time_in_millis": 105712439,
              "total_docs": 584353571,
              "total_size_in_bytes": 337520122343,
              "total_stopped_time_in_millis": 30484,
              "total_throttled_time_in_millis": 82716684,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12418,
              "total_time_in_millis": 7188249,
              "listeners": 0
            },
            "flush": {
              "total": 468,
              "periodic": 467,
              "total_time_in_millis": 519891
            },
            "warmer": {
              "current": 0,
              "total": 11941,
              "total_time_in_millis": 689
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6548,
              "hit_count": 3048,
              "miss_count": 3500,
              "cache_size": 0,
              "cache_count": 75,
              "evictions": 75
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 51,
              "memory_in_bytes": 202948300,
              "terms_memory_in_bytes": 161344939,
              "stored_fields_memory_in_bytes": 37306096,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4289357,
              "doc_values_memory_in_bytes": 7908,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108686436
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AryL4Q==",
              "generation": 471,
              "user_data": {
                "local_checkpoint": "194411532",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "4cuSVqpHQtOTyi6z5bZmag",
                "history_uuid": "jl9NJr4HSDyycENwfm5GHA",
                "sync_id": "eTMIveeHTwWx5f6DLZ57wA",
                "translog_generation": "3708",
                "max_seq_no": "194411532"
              },
              "num_docs": 194411533
            },
            "seq_no": {
              "max_seq_no": 194411532,
              "local_checkpoint": 194411532,
              "global_checkpoint": 194411532
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "9": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 194428733,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93529596477
            },
            "indexing": {
              "index_total": 194428733,
              "index_time_in_millis": 38224193,
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
              "query_total": 4538,
              "query_time_in_millis": 1188272,
              "query_current": 0,
              "fetch_total": 10,
              "fetch_time_in_millis": 522,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3263,
              "total_time_in_millis": 105305855,
              "total_docs": 584226263,
              "total_size_in_bytes": 338014655993,
              "total_stopped_time_in_millis": 413,
              "total_throttled_time_in_millis": 81868933,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12980,
              "total_time_in_millis": 6509642,
              "listeners": 0
            },
            "flush": {
              "total": 468,
              "periodic": 467,
              "total_time_in_millis": 459165
            },
            "warmer": {
              "current": 0,
              "total": 12503,
              "total_time_in_millis": 691
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6720,
              "hit_count": 3161,
              "miss_count": 3559,
              "cache_size": 0,
              "cache_count": 77,
              "evictions": 77
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 48,
              "memory_in_bytes": 208610556,
              "terms_memory_in_bytes": 166887395,
              "stored_fields_memory_in_bytes": 37423824,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4288505,
              "doc_values_memory_in_bytes": 10832,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688649
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGK9jQ==",
              "generation": 471,
              "user_data": {
                "local_checkpoint": "194428732",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "113RS-ULRZWayMmb6seErQ",
                "history_uuid": "-3pekjv6RKKMNBf9hce_Dw",
                "sync_id": "BCSj9Q3lQt26QGOtG13oXw",
                "translog_generation": "3719",
                "max_seq_no": "194428732"
              },
              "num_docs": 194428733
            },
            "seq_no": {
              "max_seq_no": 194428732,
              "local_checkpoint": 194428732,
              "global_checkpoint": 194428732
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "10": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 194414611,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93609602725
            },
            "indexing": {
              "index_total": 194414611,
              "index_time_in_millis": 39571679,
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
              "query_total": 4523,
              "query_time_in_millis": 1082729,
              "query_current": 0,
              "fetch_total": 10,
              "fetch_time_in_millis": 1692,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3418,
              "total_time_in_millis": 106184729,
              "total_docs": 587421337,
              "total_size_in_bytes": 340280922116,
              "total_stopped_time_in_millis": 4059,
              "total_throttled_time_in_millis": 81647159,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12888,
              "total_time_in_millis": 6511550,
              "listeners": 0
            },
            "flush": {
              "total": 469,
              "periodic": 468,
              "total_time_in_millis": 460677
            },
            "warmer": {
              "current": 0,
              "total": 12413,
              "total_time_in_millis": 760
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6621,
              "hit_count": 3313,
              "miss_count": 3308,
              "cache_size": 0,
              "cache_count": 75,
              "evictions": 75
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 48,
              "memory_in_bytes": 205784879,
              "terms_memory_in_bytes": 163965165,
              "stored_fields_memory_in_bytes": 37514544,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4288658,
              "doc_values_memory_in_bytes": 16512,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688453
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOwqAA==",
              "generation": 472,
              "user_data": {
                "local_checkpoint": "194414610",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "5YJDe8x4Q4O_mzN7TQX4PQ",
                "history_uuid": "ar3if7LnTDmG-I8oKcNvdQ",
                "sync_id": "5AdSwXIUTtmm3dmBHbO6pg",
                "translog_generation": "3713",
                "max_seq_no": "194414610"
              },
              "num_docs": 194414611
            },
            "seq_no": {
              "max_seq_no": 194414610,
              "local_checkpoint": 194414610,
              "global_checkpoint": 194414610
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "11": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 194403950,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93376543794
            },
            "indexing": {
              "index_total": 194403950,
              "index_time_in_millis": 41153084,
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
              "query_total": 4538,
              "query_time_in_millis": 936831,
              "query_current": 0,
              "fetch_total": 9,
              "fetch_time_in_millis": 481,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3340,
              "total_time_in_millis": 105626635,
              "total_docs": 589110642,
              "total_size_in_bytes": 340897005524,
              "total_stopped_time_in_millis": 29378,
              "total_throttled_time_in_millis": 81010374,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12389,
              "total_time_in_millis": 7170188,
              "listeners": 0
            },
            "flush": {
              "total": 467,
              "periodic": 466,
              "total_time_in_millis": 505362
            },
            "warmer": {
              "current": 0,
              "total": 11912,
              "total_time_in_millis": 835
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6915,
              "hit_count": 3280,
              "miss_count": 3635,
              "cache_size": 0,
              "cache_count": 69,
              "evictions": 69
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 41,
              "memory_in_bytes": 198933181,
              "terms_memory_in_bytes": 157168241,
              "stored_fields_memory_in_bytes": 37465944,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4288408,
              "doc_values_memory_in_bytes": 10588,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108687416
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBu3Jg==",
              "generation": 471,
              "user_data": {
                "local_checkpoint": "194403949",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "MftnCUUARyKx6o96nEgNnw",
                "history_uuid": "Ic-le1M4QxOc_AvmC4CnUQ",
                "sync_id": "XMLZElbmSOaaZnZD5enbeA",
                "translog_generation": "3706",
                "max_seq_no": "194403949"
              },
              "num_docs": 194403950
            },
            "seq_no": {
              "max_seq_no": 194403949,
              "local_checkpoint": 194403949,
              "global_checkpoint": 194403949
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "12": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 194390391,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93296615917
            },
            "indexing": {
              "index_total": 194390391,
              "index_time_in_millis": 39078137,
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
              "query_total": 4538,
              "query_time_in_millis": 1022791,
              "query_current": 0,
              "fetch_total": 9,
              "fetch_time_in_millis": 621,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3244,
              "total_time_in_millis": 105576367,
              "total_docs": 585429568,
              "total_size_in_bytes": 338325451857,
              "total_stopped_time_in_millis": 25426,
              "total_throttled_time_in_millis": 82544575,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12369,
              "total_time_in_millis": 7196840,
              "listeners": 0
            },
            "flush": {
              "total": 469,
              "periodic": 468,
              "total_time_in_millis": 528980
            },
            "warmer": {
              "current": 0,
              "total": 11892,
              "total_time_in_millis": 629
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6420,
              "hit_count": 2988,
              "miss_count": 3432,
              "cache_size": 0,
              "cache_count": 67,
              "evictions": 67
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 45,
              "memory_in_bytes": 202610682,
              "terms_memory_in_bytes": 160935350,
              "stored_fields_memory_in_bytes": 37381400,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4286824,
              "doc_values_memory_in_bytes": 7108,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108686322
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AryL4w==",
              "generation": 472,
              "user_data": {
                "local_checkpoint": "194390390",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "ZguRaLVVRMu-jO4NGcCd-A",
                "history_uuid": "YiIyH1pSRRSKWltF0g11aA",
                "sync_id": "Yk2pWx7HRuijLXAwlEE5NA",
                "translog_generation": "3721",
                "max_seq_no": "194390390"
              },
              "num_docs": 194390391
            },
            "seq_no": {
              "max_seq_no": 194390390,
              "local_checkpoint": 194390390,
              "global_checkpoint": 194390390
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "13": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 194413831,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93357043622
            },
            "indexing": {
              "index_total": 194413831,
              "index_time_in_millis": 38911093,
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
              "query_total": 4538,
              "query_time_in_millis": 1149813,
              "query_current": 0,
              "fetch_total": 25,
              "fetch_time_in_millis": 749,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3386,
              "total_time_in_millis": 105177037,
              "total_docs": 589207466,
              "total_size_in_bytes": 340957266942,
              "total_stopped_time_in_millis": 5405,
              "total_throttled_time_in_millis": 81633608,
              "total_auto_throttle_in_bytes": 6291456
            },
            "refresh": {
              "total": 12961,
              "total_time_in_millis": 6489175,
              "listeners": 0
            },
            "flush": {
              "total": 469,
              "periodic": 468,
              "total_time_in_millis": 448564
            },
            "warmer": {
              "current": 0,
              "total": 12483,
              "total_time_in_millis": 706
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6924,
              "hit_count": 3305,
              "miss_count": 3619,
              "cache_size": 0,
              "cache_count": 71,
              "evictions": 71
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 46,
              "memory_in_bytes": 198940656,
              "terms_memory_in_bytes": 157156893,
              "stored_fields_memory_in_bytes": 37488808,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4287515,
              "doc_values_memory_in_bytes": 7440,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688646
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGLLSA==",
              "generation": 473,
              "user_data": {
                "local_checkpoint": "194413830",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "vWu6iXcaSAGBbQ6PXi7zXA",
                "history_uuid": "jn_SnfgXSmmnN3fGBixMtg",
                "sync_id": "6bws1-0ER_a_qGPX42qr_w",
                "translog_generation": "3715",
                "max_seq_no": "194413830"
              },
              "num_docs": 194413831
            },
            "seq_no": {
              "max_seq_no": 194413830,
              "local_checkpoint": 194413830,
              "global_checkpoint": 194413830
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "14": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 194384810,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 94122859635
            },
            "indexing": {
              "index_total": 194384810,
              "index_time_in_millis": 39989491,
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
              "query_total": 4523,
              "query_time_in_millis": 1045921,
              "query_current": 0,
              "fetch_total": 12,
              "fetch_time_in_millis": 1038,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3642,
              "total_time_in_millis": 104255112,
              "total_docs": 586575478,
              "total_size_in_bytes": 340627213302,
              "total_stopped_time_in_millis": 11894,
              "total_throttled_time_in_millis": 80192559,
              "total_auto_throttle_in_bytes": 5719505
            },
            "refresh": {
              "total": 12858,
              "total_time_in_millis": 6417562,
              "listeners": 0
            },
            "flush": {
              "total": 468,
              "periodic": 467,
              "total_time_in_millis": 479997
            },
            "warmer": {
              "current": 0,
              "total": 12381,
              "total_time_in_millis": 790
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 7260,
              "hit_count": 3582,
              "miss_count": 3678,
              "cache_size": 0,
              "cache_count": 78,
              "evictions": 78
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 50,
              "memory_in_bytes": 217122250,
              "terms_memory_in_bytes": 175131730,
              "stored_fields_memory_in_bytes": 37681408,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4293592,
              "doc_values_memory_in_bytes": 15520,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688429
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOwq7g==",
              "generation": 472,
              "user_data": {
                "local_checkpoint": "194384809",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "bfwrcKwXQWyLUGe7JNc2qg",
                "history_uuid": "AjVDooZJQb-NveONgIZuzg",
                "sync_id": "CKbvm3wgSk6lmd_-lMRRuw",
                "translog_generation": "3711",
                "max_seq_no": "194384809"
              },
              "num_docs": 194384810
            },
            "seq_no": {
              "max_seq_no": 194384809,
              "local_checkpoint": 194384809,
              "global_checkpoint": 194384809
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "15": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 194404339,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 93475754363
            },
            "indexing": {
              "index_total": 194404339,
              "index_time_in_millis": 41489689,
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
              "query_total": 4538,
              "query_time_in_millis": 897324,
              "query_current": 0,
              "fetch_total": 13,
              "fetch_time_in_millis": 480,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3503,
              "total_time_in_millis": 106224822,
              "total_docs": 591008290,
              "total_size_in_bytes": 342392423739,
              "total_stopped_time_in_millis": 11111,
              "total_throttled_time_in_millis": 81777106,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12356,
              "total_time_in_millis": 7053079,
              "listeners": 0
            },
            "flush": {
              "total": 469,
              "periodic": 468,
              "total_time_in_millis": 535539
            },
            "warmer": {
              "current": 0,
              "total": 11877,
              "total_time_in_millis": 639
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 6936,
              "hit_count": 3235,
              "miss_count": 3701,
              "cache_size": 0,
              "cache_count": 71,
              "evictions": 71
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 50,
              "memory_in_bytes": 202043884,
              "terms_memory_in_bytes": 160166341,
              "stored_fields_memory_in_bytes": 37576200,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 4293631,
              "doc_values_memory_in_bytes": 7712,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002521,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108687356
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBu59g==",
              "generation": 473,
              "user_data": {
                "local_checkpoint": "194404338",
                "max_unsafe_auto_id_timestamp": "1542672002521",
                "translog_uuid": "6LHXnjWbSpGG5NF5GObcJg",
                "history_uuid": "yPVt6svHQTa03YwNaOgpZw",
                "sync_id": "XG1wuH62T4WOlATVxh3vTw",
                "translog_generation": "3721",
                "max_seq_no": "194404338"
              },
              "num_docs": 194404339
            },
            "seq_no": {
              "max_seq_no": 194404338,
              "local_checkpoint": 194404338,
              "global_checkpoint": 194404338
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-es-6-2018.11.16": {
      "uuid": "8-NEnibNTOC1UFfC8lEa1w",
      "primaries": {
        "docs": {
          "count": 158613,
          "deleted": 342
        },
        "store": {
          "size_in_bytes": 107063984
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 9581,
          "query_time_in_millis": 1650,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 3,
          "total_time_in_millis": 0,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 1,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 17960,
          "hit_count": 1006,
          "miss_count": 16954,
          "cache_size": 0,
          "cache_count": 4,
          "evictions": 4
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 13,
          "memory_in_bytes": 300646,
          "terms_memory_in_bytes": 94662,
          "stored_fields_memory_in_bytes": 22024,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 46252,
          "doc_values_memory_in_bytes": 137708,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542357882592,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 275,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 275,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 5260,
          "miss_count": 83
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 317226,
          "deleted": 684
        },
        "store": {
          "size_in_bytes": 214127968
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 19161,
          "query_time_in_millis": 3637,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 6,
          "total_time_in_millis": 1,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 2,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 35908,
          "hit_count": 1855,
          "miss_count": 34053,
          "cache_size": 0,
          "cache_count": 8,
          "evictions": 8
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 26,
          "memory_in_bytes": 601292,
          "terms_memory_in_bytes": 189324,
          "stored_fields_memory_in_bytes": 44048,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 92504,
          "doc_values_memory_in_bytes": 275416,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542357882592,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 550,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 550,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 10365,
          "miss_count": 167
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 158613,
              "deleted": 342
            },
            "store": {
              "size_in_bytes": 107063984
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 9580,
              "query_time_in_millis": 1987,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 1,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 17948,
              "hit_count": 849,
              "miss_count": 17099,
              "cache_size": 0,
              "cache_count": 4,
              "evictions": 4
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 13,
              "memory_in_bytes": 300646,
              "terms_memory_in_bytes": 94662,
              "stored_fields_memory_in_bytes": 22024,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 46252,
              "doc_values_memory_in_bytes": 137708,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542357882592,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 275,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 275,
              "earliest_last_modified_age": 235776077
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5105,
              "miss_count": 84
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "vJYLqvxw1OxRtw75eIaFLQ==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "584658",
                "max_unsafe_auto_id_timestamp": "1542357882592",
                "translog_uuid": "hF0SzusqTf-6GaboVjhNXg",
                "history_uuid": "IyV5her4R1S4WZN6iMj_-g",
                "sync_id": "DjsE1xr-TSqfT8ErUMa72w",
                "translog_generation": "1",
                "max_seq_no": "584658"
              },
              "num_docs": 158613
            },
            "seq_no": {
              "max_seq_no": 584658,
              "local_checkpoint": 584658,
              "global_checkpoint": 584658
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 158613,
              "deleted": 342
            },
            "store": {
              "size_in_bytes": 107063984
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 9581,
              "query_time_in_millis": 1650,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 0,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 17960,
              "hit_count": 1006,
              "miss_count": 16954,
              "cache_size": 0,
              "cache_count": 4,
              "evictions": 4
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 13,
              "memory_in_bytes": 300646,
              "terms_memory_in_bytes": 94662,
              "stored_fields_memory_in_bytes": 22024,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 46252,
              "doc_values_memory_in_bytes": 137708,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542357882592,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 275,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 275,
              "earliest_last_modified_age": 236337771
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5260,
              "miss_count": 83
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "ehuu6qAbGslqqS83pWABSQ==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "584658",
                "max_unsafe_auto_id_timestamp": "1542357882592",
                "translog_uuid": "5Z7b7i89TMyeBaaR_e1pXA",
                "history_uuid": "IyV5her4R1S4WZN6iMj_-g",
                "sync_id": "DjsE1xr-TSqfT8ErUMa72w",
                "translog_generation": "1",
                "max_seq_no": "584658"
              },
              "num_docs": 158613
            },
            "seq_no": {
              "max_seq_no": 584658,
              "local_checkpoint": 584658,
              "global_checkpoint": 584658
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-es-6-2018.11.19": {
      "uuid": "8NxvV2PARzmxAQbUSdc0rw",
      "primaries": {
        "docs": {
          "count": 226434,
          "deleted": 632
        },
        "store": {
          "size_in_bytes": 162509045
        },
        "indexing": {
          "index_total": 411584,
          "index_time_in_millis": 145318,
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
          "query_total": 9581,
          "query_time_in_millis": 2391,
          "query_current": 0,
          "fetch_total": 371,
          "fetch_time_in_millis": 118,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 2156,
          "total_time_in_millis": 492147,
          "total_docs": 5099047,
          "total_size_in_bytes": 4668815860,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 97,
          "total_auto_throttle_in_bytes": 19065018
        },
        "refresh": {
          "total": 20702,
          "total_time_in_millis": 341045,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 64
        },
        "warmer": {
          "current": 0,
          "total": 16783,
          "total_time_in_millis": 11870
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 16859,
          "hit_count": 1700,
          "miss_count": 15159,
          "cache_size": 0,
          "cache_count": 21,
          "evictions": 21
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 11,
          "memory_in_bytes": 372598,
          "terms_memory_in_bytes": 100476,
          "stored_fields_memory_in_bytes": 28592,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 63566,
          "doc_values_memory_in_bytes": 179964,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542632166544,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 55,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 55,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 5180,
          "miss_count": 91
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 124
        }
      },
      "total": {
        "docs": {
          "count": 452868,
          "deleted": 1342
        },
        "store": {
          "size_in_bytes": 325897935
        },
        "indexing": {
          "index_total": 822555,
          "index_time_in_millis": 315099,
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
          "query_total": 19163,
          "query_time_in_millis": 4847,
          "query_current": 0,
          "fetch_total": 747,
          "fetch_time_in_millis": 220,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 4293,
          "total_time_in_millis": 1002829,
          "total_docs": 10262234,
          "total_size_in_bytes": 9402999526,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 97,
          "total_auto_throttle_in_bytes": 40036538
        },
        "refresh": {
          "total": 41235,
          "total_time_in_millis": 712314,
          "listeners": 0
        },
        "flush": {
          "total": 3,
          "periodic": 1,
          "total_time_in_millis": 234
        },
        "warmer": {
          "current": 0,
          "total": 33403,
          "total_time_in_millis": 23540
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 39232,
          "hit_count": 3742,
          "miss_count": 35490,
          "cache_size": 0,
          "cache_count": 45,
          "evictions": 45
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 26,
          "memory_in_bytes": 764255,
          "terms_memory_in_bytes": 216695,
          "stored_fields_memory_in_bytes": 58192,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 129712,
          "doc_values_memory_in_bytes": 359656,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542632848051,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 110,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 10354,
          "miss_count": 178
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 2626
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 226434,
              "deleted": 710
            },
            "store": {
              "size_in_bytes": 163388890
            },
            "indexing": {
              "index_total": 410971,
              "index_time_in_millis": 169781,
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
              "query_total": 9582,
              "query_time_in_millis": 2456,
              "query_current": 0,
              "fetch_total": 376,
              "fetch_time_in_millis": 102,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2137,
              "total_time_in_millis": 510682,
              "total_docs": 5163187,
              "total_size_in_bytes": 4734183666,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 20533,
              "total_time_in_millis": 371269,
              "listeners": 0
            },
            "flush": {
              "total": 2,
              "periodic": 1,
              "total_time_in_millis": 170
            },
            "warmer": {
              "current": 0,
              "total": 16620,
              "total_time_in_millis": 11670
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 22373,
              "hit_count": 2042,
              "miss_count": 20331,
              "cache_size": 0,
              "cache_count": 24,
              "evictions": 24
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 15,
              "memory_in_bytes": 391657,
              "terms_memory_in_bytes": 116219,
              "stored_fields_memory_in_bytes": 29600,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 66146,
              "doc_values_memory_in_bytes": 179692,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632848051,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195090166
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5174,
              "miss_count": 87
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 2502
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBh6mQ==",
              "generation": 13,
              "user_data": {
                "local_checkpoint": "826564",
                "max_unsafe_auto_id_timestamp": "1542632848051",
                "translog_uuid": "YK2wiDKhQy2Bo9YoOdooMQ",
                "history_uuid": "cUXu0iK-SGu474kFq4ypIA",
                "sync_id": "xOvnk-iTQN2mgCf3YLcUNw",
                "translog_generation": "15",
                "max_seq_no": "826564"
              },
              "num_docs": 226434
            },
            "seq_no": {
              "max_seq_no": 826564,
              "local_checkpoint": 826564,
              "global_checkpoint": 826564
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 226434,
              "deleted": 632
            },
            "store": {
              "size_in_bytes": 162509045
            },
            "indexing": {
              "index_total": 411584,
              "index_time_in_millis": 145318,
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
              "query_total": 9581,
              "query_time_in_millis": 2391,
              "query_current": 0,
              "fetch_total": 371,
              "fetch_time_in_millis": 118,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2156,
              "total_time_in_millis": 492147,
              "total_docs": 5099047,
              "total_size_in_bytes": 4668815860,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 97,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 20702,
              "total_time_in_millis": 341045,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 64
            },
            "warmer": {
              "current": 0,
              "total": 16783,
              "total_time_in_millis": 11870
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 16859,
              "hit_count": 1700,
              "miss_count": 15159,
              "cache_size": 0,
              "cache_count": 21,
              "evictions": 21
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 11,
              "memory_in_bytes": 372598,
              "terms_memory_in_bytes": 100476,
              "stored_fields_memory_in_bytes": 28592,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 63566,
              "doc_values_memory_in_bytes": 179964,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632166544,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195090211
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5180,
              "miss_count": 91
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 124
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWF7Mbg==",
              "generation": 11,
              "user_data": {
                "local_checkpoint": "826564",
                "max_unsafe_auto_id_timestamp": "1542632166544",
                "translog_uuid": "qc_aDRDhQnOy-NvVPlk37g",
                "history_uuid": "cUXu0iK-SGu474kFq4ypIA",
                "sync_id": "xOvnk-iTQN2mgCf3YLcUNw",
                "translog_generation": "17",
                "max_seq_no": "826564"
              },
              "num_docs": 226434
            },
            "seq_no": {
              "max_seq_no": 826564,
              "local_checkpoint": 826564,
              "global_checkpoint": 826564
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-kibana-6-2018.11.16": {
      "uuid": "ZjyLa1zQSrG-JLgJ66DciA",
      "primaries": {
        "docs": {
          "count": 8607,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2497080
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 427,
          "query_time_in_millis": 111,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 3,
          "total_time_in_millis": 1,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 1,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 5,
          "memory_in_bytes": 32516,
          "terms_memory_in_bytes": 23607,
          "stored_fields_memory_in_bytes": 2064,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 1233,
          "doc_values_memory_in_bytes": 5612,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542412792430,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 110,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 405,
          "miss_count": 1
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 17214,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 4994160
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 860,
          "query_time_in_millis": 190,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 6,
          "total_time_in_millis": 2,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 2,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 10,
          "memory_in_bytes": 65032,
          "terms_memory_in_bytes": 47214,
          "stored_fields_memory_in_bytes": 4128,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 2466,
          "doc_values_memory_in_bytes": 11224,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542412792430,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 330,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 330,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 801,
          "miss_count": 2
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 8607,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2497080
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 427,
              "query_time_in_millis": 111,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 1,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 5,
              "memory_in_bytes": 32516,
              "terms_memory_in_bytes": 23607,
              "stored_fields_memory_in_bytes": 2064,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1233,
              "doc_values_memory_in_bytes": 5612,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542412792430,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 110,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 110,
              "earliest_last_modified_age": 234487810
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 405,
              "miss_count": 1
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbObggw==",
              "generation": 12,
              "user_data": {
                "local_checkpoint": "8606",
                "max_unsafe_auto_id_timestamp": "1542412792430",
                "translog_uuid": "HpVftRneRCar8CdB5W6seA",
                "history_uuid": "-XjjREv9RcG4QsUKC2M76A",
                "sync_id": "O0OjqKbBSMKf6dGjhiU6hA",
                "translog_generation": "1",
                "max_seq_no": "8606"
              },
              "num_docs": 8607
            },
            "seq_no": {
              "max_seq_no": 8606,
              "local_checkpoint": 8606,
              "global_checkpoint": 8606
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 8607,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2497080
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 433,
              "query_time_in_millis": 79,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 1,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 5,
              "memory_in_bytes": 32516,
              "terms_memory_in_bytes": 23607,
              "stored_fields_memory_in_bytes": 2064,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1233,
              "doc_values_memory_in_bytes": 5612,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542412792430,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 220,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 220,
              "earliest_last_modified_age": 235775019
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 396,
              "miss_count": 1
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "vJYLqvxw1OxRtw75eIaFLw==",
              "generation": 10,
              "user_data": {
                "local_checkpoint": "8606",
                "max_unsafe_auto_id_timestamp": "1542412792430",
                "translog_uuid": "SY2D80fuTOiFO1YSzF7Kkg",
                "history_uuid": "-XjjREv9RcG4QsUKC2M76A",
                "sync_id": "O0OjqKbBSMKf6dGjhiU6hA",
                "translog_generation": "1",
                "max_seq_no": "8606"
              },
              "num_docs": 8607
            },
            "seq_no": {
              "max_seq_no": 8606,
              "local_checkpoint": 8606,
              "global_checkpoint": 8606
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-kibana-6-2018.11.17": {
      "uuid": "OP9m88s_RCiSZH6TvRmNFg",
      "primaries": {
        "docs": {
          "count": 8625,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2513697
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 426,
          "query_time_in_millis": 106,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 3,
          "total_time_in_millis": 7,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 1,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 4,
          "memory_in_bytes": 25058,
          "terms_memory_in_bytes": 19320,
          "stored_fields_memory_in_bytes": 1624,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 1186,
          "doc_values_memory_in_bytes": 2928,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542438741015,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 110,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 401,
          "miss_count": 1
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 17250,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 5027394
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 860,
          "query_time_in_millis": 206,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 6,
          "total_time_in_millis": 7,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 2,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 8,
          "memory_in_bytes": 50116,
          "terms_memory_in_bytes": 38640,
          "stored_fields_memory_in_bytes": 3248,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 2372,
          "doc_values_memory_in_bytes": 5856,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542438741015,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 220,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 220,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 801,
          "miss_count": 2
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 8625,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2513697
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 426,
              "query_time_in_millis": 106,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 7,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 4,
              "memory_in_bytes": 25058,
              "terms_memory_in_bytes": 19320,
              "stored_fields_memory_in_bytes": 1624,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1186,
              "doc_values_memory_in_bytes": 2928,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542438741015,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 110,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 110,
              "earliest_last_modified_age": 234487050
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 401,
              "miss_count": 1
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbObgig==",
              "generation": 8,
              "user_data": {
                "local_checkpoint": "8624",
                "max_unsafe_auto_id_timestamp": "1542438741015",
                "translog_uuid": "q9wi99ANQjSeN2efgQxazQ",
                "history_uuid": "kAaDCmceTQGkrawjr-E-JA",
                "sync_id": "Ywukoxe_QAiOUxwBdMYigA",
                "translog_generation": "1",
                "max_seq_no": "8624"
              },
              "num_docs": 8625
            },
            "seq_no": {
              "max_seq_no": 8624,
              "local_checkpoint": 8624,
              "global_checkpoint": 8624
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 8625,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2513697
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 434,
              "query_time_in_millis": 100,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 0,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 4,
              "memory_in_bytes": 25058,
              "terms_memory_in_bytes": 19320,
              "stored_fields_memory_in_bytes": 1624,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1186,
              "doc_values_memory_in_bytes": 2928,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542438741015,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 110,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 110,
              "earliest_last_modified_age": 234556206
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 400,
              "miss_count": 1
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWF0klw==",
              "generation": 8,
              "user_data": {
                "local_checkpoint": "8624",
                "max_unsafe_auto_id_timestamp": "1542438741015",
                "translog_uuid": "gvztl71RTP-SBpCJVFjwOQ",
                "history_uuid": "kAaDCmceTQGkrawjr-E-JA",
                "sync_id": "Ywukoxe_QAiOUxwBdMYigA",
                "translog_generation": "1",
                "max_seq_no": "8624"
              },
              "num_docs": 8625
            },
            "seq_no": {
              "max_seq_no": 8624,
              "local_checkpoint": 8624,
              "global_checkpoint": 8624
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-kibana-6-2018.11.18": {
      "uuid": "g4GS2xVpRWC6xkU-VBFrhg",
      "primaries": {
        "docs": {
          "count": 8638,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2341087
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 429,
          "query_time_in_millis": 112,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 3,
          "total_time_in_millis": 0,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 1
        },
        "warmer": {
          "current": 0,
          "total": 1,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 7,
          "memory_in_bytes": 40641,
          "terms_memory_in_bytes": 31976,
          "stored_fields_memory_in_bytes": 2640,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 1461,
          "doc_values_memory_in_bytes": 4564,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 220,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 220,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 403,
          "miss_count": 1
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 20
        }
      },
      "total": {
        "docs": {
          "count": 17276,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 4682174
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 860,
          "query_time_in_millis": 208,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 6,
          "total_time_in_millis": 0,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 1
        },
        "warmer": {
          "current": 0,
          "total": 2,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 14,
          "memory_in_bytes": 81282,
          "terms_memory_in_bytes": 63952,
          "stored_fields_memory_in_bytes": 5280,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 2922,
          "doc_values_memory_in_bytes": 9128,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 330,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 330,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 801,
          "miss_count": 2
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 20
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 8638,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2341087
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 429,
              "query_time_in_millis": 112,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 0,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 1
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 7,
              "memory_in_bytes": 40641,
              "terms_memory_in_bytes": 31976,
              "stored_fields_memory_in_bytes": 2640,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1461,
              "doc_values_memory_in_bytes": 4564,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 220,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 220,
              "earliest_last_modified_age": 281489822
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 403,
              "miss_count": 1
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 20
            },
            "commit": {
              "id": "ivoc6vV0IkIyt9Z35aNaPw==",
              "generation": 4,
              "user_data": {
                "local_checkpoint": "8637",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "zpi_A8YcT66is-crC7w1wQ",
                "history_uuid": "prpmTpkbTDe8c5oEbppWHw",
                "sync_id": "ii0uX_zbT22YG_AojGspUQ",
                "translog_generation": "3",
                "max_seq_no": "8637"
              },
              "num_docs": 8638
            },
            "seq_no": {
              "max_seq_no": 8637,
              "local_checkpoint": 8637,
              "global_checkpoint": 8637
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 8638,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2341087
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 431,
              "query_time_in_millis": 96,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 0,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 7,
              "memory_in_bytes": 40641,
              "terms_memory_in_bytes": 31976,
              "stored_fields_memory_in_bytes": 2640,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1461,
              "doc_values_memory_in_bytes": 4564,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 110,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 110,
              "earliest_last_modified_age": 234560884
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 398,
              "miss_count": 1
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWF0kkw==",
              "generation": 5,
              "user_data": {
                "local_checkpoint": "8637",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "dpIdaFAXRvORftt8BCoFXw",
                "history_uuid": "prpmTpkbTDe8c5oEbppWHw",
                "sync_id": "ii0uX_zbT22YG_AojGspUQ",
                "translog_generation": "1",
                "max_seq_no": "8637"
              },
              "num_docs": 8638
            },
            "seq_no": {
              "max_seq_no": 8637,
              "local_checkpoint": 8637,
              "global_checkpoint": 8637
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    "metricbeat-6.5.0-2018.11.19": {
      "uuid": "Z0Bi-kwyRSmvVeQerCn6dQ",
      "primaries": {
        "docs": {
          "count": 1472711,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 1046524474
        },
        "indexing": {
          "index_total": 1451128,
          "index_time_in_millis": 584702,
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
          "query_total": 514,
          "query_time_in_millis": 8342,
          "query_current": 0,
          "fetch_total": 1,
          "fetch_time_in_millis": 2,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 4232,
          "total_time_in_millis": 762795,
          "total_docs": 11087935,
          "total_size_in_bytes": 11857317563,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 14030,
          "total_auto_throttle_in_bytes": 92032040
        },
        "refresh": {
          "total": 25459,
          "total_time_in_millis": 1206173,
          "listeners": 0
        },
        "flush": {
          "total": 5,
          "periodic": 0,
          "total_time_in_millis": 275
        },
        "warmer": {
          "current": 0,
          "total": 25448,
          "total_time_in_millis": 12182
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 2547,
          "hit_count": 153,
          "miss_count": 2394,
          "cache_size": 0,
          "cache_count": 12,
          "evictions": 12
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 77,
          "memory_in_bytes": 4505041,
          "terms_memory_in_bytes": 1288825,
          "stored_fields_memory_in_bytes": 433856,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 225900,
          "doc_values_memory_in_bytes": 2556460,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542632902546,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 275,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 275,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 56,
          "miss_count": 357
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 20
        }
      },
      "total": {
        "docs": {
          "count": 2945422,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2089396388
        },
        "indexing": {
          "index_total": 2905706,
          "index_time_in_millis": 1159141,
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
          "query_total": 1060,
          "query_time_in_millis": 16985,
          "query_current": 0,
          "fetch_total": 2,
          "fetch_time_in_millis": 3,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 8351,
          "total_time_in_millis": 1491661,
          "total_docs": 22273244,
          "total_size_in_bytes": 23717541776,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 31934,
          "total_auto_throttle_in_bytes": 183890762
        },
        "refresh": {
          "total": 50794,
          "total_time_in_millis": 2442940,
          "listeners": 0
        },
        "flush": {
          "total": 10,
          "periodic": 0,
          "total_time_in_millis": 566
        },
        "warmer": {
          "current": 0,
          "total": 50774,
          "total_time_in_millis": 24848
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 4711,
          "hit_count": 273,
          "miss_count": 4438,
          "cache_size": 0,
          "cache_count": 22,
          "evictions": 22
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 159,
          "memory_in_bytes": 8864483,
          "terms_memory_in_bytes": 2608219,
          "stored_fields_memory_in_bytes": 869008,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 450156,
          "doc_values_memory_in_bytes": 4937100,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542632902546,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 550,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 550,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 119,
          "miss_count": 706
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 52
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 294463,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 210233295
            },
            "indexing": {
              "index_total": 288847,
              "index_time_in_millis": 117859,
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
              "query_total": 107,
              "query_time_in_millis": 1483,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 849,
              "total_time_in_millis": 154087,
              "total_docs": 2183140,
              "total_size_in_bytes": 2342209636,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 1946,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 5103,
              "total_time_in_millis": 258029,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 57
            },
            "warmer": {
              "current": 0,
              "total": 5101,
              "total_time_in_millis": 2359
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 635,
              "hit_count": 26,
              "miss_count": 609,
              "cache_size": 0,
              "cache_count": 2,
              "evictions": 2
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 15,
              "memory_in_bytes": 900838,
              "terms_memory_in_bytes": 249377,
              "stored_fields_memory_in_bytes": 85360,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 45897,
              "doc_values_memory_in_bytes": 520204,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632902546,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195087673
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 9,
              "miss_count": 73
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 32
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBh6pA==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "294462",
                "max_unsafe_auto_id_timestamp": "1542632902546",
                "translog_uuid": "tXHNYnTwS0SIln5U4h1H5g",
                "history_uuid": "XAXz4-S6ROC0Yl8GvDvHSg",
                "sync_id": "AEfobLmDT9-Z4vQ3tHhg5g",
                "translog_generation": "9",
                "max_seq_no": "294462"
              },
              "num_docs": 294463
            },
            "seq_no": {
              "max_seq_no": 294462,
              "local_checkpoint": 294462,
              "global_checkpoint": 294462
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 294463,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 209990876
            },
            "indexing": {
              "index_total": 292166,
              "index_time_in_millis": 120868,
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
              "query_total": 105,
              "query_time_in_millis": 2270,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 915,
              "total_time_in_millis": 169202,
              "total_docs": 2288912,
              "total_size_in_bytes": 2455323459,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 5175,
              "total_time_in_millis": 269589,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 47
            },
            "warmer": {
              "current": 0,
              "total": 5172,
              "total_time_in_millis": 2737
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 596,
              "hit_count": 23,
              "miss_count": 573,
              "cache_size": 0,
              "cache_count": 2,
              "evictions": 2
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 18,
              "memory_in_bytes": 840020,
              "terms_memory_in_bytes": 286844,
              "stored_fields_memory_in_bytes": 86800,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 47040,
              "doc_values_memory_in_bytes": 419336,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632821622,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195087689
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 10,
              "miss_count": 73
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4ArltKQ==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "294462",
                "max_unsafe_auto_id_timestamp": "1542632821622",
                "translog_uuid": "NW5W09mSTJG25HugGRXDSw",
                "history_uuid": "XAXz4-S6ROC0Yl8GvDvHSg",
                "sync_id": "AEfobLmDT9-Z4vQ3tHhg5g",
                "translog_generation": "13",
                "max_seq_no": "294462"
              },
              "num_docs": 294463
            },
            "seq_no": {
              "max_seq_no": 294462,
              "local_checkpoint": 294462,
              "global_checkpoint": 294462
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "1": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 294501,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 210623531
            },
            "indexing": {
              "index_total": 288847,
              "index_time_in_millis": 116965,
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
              "query_total": 101,
              "query_time_in_millis": 1423,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 817,
              "total_time_in_millis": 154342,
              "total_docs": 2119054,
              "total_size_in_bytes": 2294153934,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 3510,
              "total_auto_throttle_in_bytes": 17331834
            },
            "refresh": {
              "total": 5068,
              "total_time_in_millis": 234609,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 46
            },
            "warmer": {
              "current": 0,
              "total": 5066,
              "total_time_in_millis": 2284
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 567,
              "hit_count": 25,
              "miss_count": 542,
              "cache_size": 0,
              "cache_count": 2,
              "evictions": 2
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 14,
              "memory_in_bytes": 882841,
              "terms_memory_in_bytes": 242622,
              "stored_fields_memory_in_bytes": 86952,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 44547,
              "doc_values_memory_in_bytes": 508720,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632892539,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195086865
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 9,
              "miss_count": 73
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOgx2Q==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "294500",
                "max_unsafe_auto_id_timestamp": "1542632892539",
                "translog_uuid": "faTS1m0LSselFVCiZxa0fA",
                "history_uuid": "rJPFQaycQQO9PWVUwvuedw",
                "sync_id": "q0MJu93tTPC2hK_Y_Gs1zA",
                "translog_generation": "9",
                "max_seq_no": "294500"
              },
              "num_docs": 294501
            },
            "seq_no": {
              "max_seq_no": 294500,
              "local_checkpoint": 294500,
              "global_checkpoint": 294500
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 294501,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 210529083
            },
            "indexing": {
              "index_total": 292134,
              "index_time_in_millis": 118992,
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
              "query_total": 111,
              "query_time_in_millis": 1434,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 816,
              "total_time_in_millis": 149266,
              "total_docs": 2190944,
              "total_size_in_bytes": 2345370733,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 1914,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 5065,
              "total_time_in_millis": 244700,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 51
            },
            "warmer": {
              "current": 0,
              "total": 5064,
              "total_time_in_millis": 2541
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 494,
              "hit_count": 21,
              "miss_count": 473,
              "cache_size": 0,
              "cache_count": 2,
              "evictions": 2
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 17,
              "memory_in_bytes": 891181,
              "terms_memory_in_bytes": 269394,
              "stored_fields_memory_in_bytes": 87680,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 45295,
              "doc_values_memory_in_bytes": 488812,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632826615,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195086853
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 16,
              "miss_count": 67
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4ArltMQ==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "294500",
                "max_unsafe_auto_id_timestamp": "1542632826615",
                "translog_uuid": "a96eGhxESiCY6vrf2OEv5A",
                "history_uuid": "rJPFQaycQQO9PWVUwvuedw",
                "sync_id": "q0MJu93tTPC2hK_Y_Gs1zA",
                "translog_generation": "9",
                "max_seq_no": "294500"
              },
              "num_docs": 294501
            },
            "seq_no": {
              "max_seq_no": 294500,
              "local_checkpoint": 294500,
              "global_checkpoint": 294500
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "2": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 295411,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 211504241
            },
            "indexing": {
              "index_total": 289769,
              "index_time_in_millis": 115178,
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
              "query_total": 101,
              "query_time_in_millis": 1901,
              "query_current": 0,
              "fetch_total": 1,
              "fetch_time_in_millis": 2,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 815,
              "total_time_in_millis": 152665,
              "total_docs": 2230779,
              "total_size_in_bytes": 2371102927,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 3891,
              "total_auto_throttle_in_bytes": 17331834
            },
            "refresh": {
              "total": 5054,
              "total_time_in_millis": 227639,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 50
            },
            "warmer": {
              "current": 0,
              "total": 5053,
              "total_time_in_millis": 2168
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 682,
              "hit_count": 55,
              "miss_count": 627,
              "cache_size": 0,
              "cache_count": 4,
              "evictions": 4
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 20,
              "memory_in_bytes": 981415,
              "terms_memory_in_bytes": 318920,
              "stored_fields_memory_in_bytes": 89016,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 47639,
              "doc_values_memory_in_bytes": 525840,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632892539,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195086864
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 12,
              "miss_count": 70
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOgx2g==",
              "generation": 8,
              "user_data": {
                "local_checkpoint": "295410",
                "max_unsafe_auto_id_timestamp": "1542632892539",
                "translog_uuid": "TsSgTRMzQQ6EKfZlR6Itww",
                "history_uuid": "W8K4_wQmQTKCFXlQFenItg",
                "sync_id": "tOLA_jVUSaecDwapDkEhIQ",
                "translog_generation": "9",
                "max_seq_no": "295410"
              },
              "num_docs": 295411
            },
            "seq_no": {
              "max_seq_no": 295410,
              "local_checkpoint": 295410,
              "global_checkpoint": 295410
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 295411,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 206533573
            },
            "indexing": {
              "index_total": 292897,
              "index_time_in_millis": 115162,
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
              "query_total": 111,
              "query_time_in_millis": 1666,
              "query_current": 0,
              "fetch_total": 1,
              "fetch_time_in_millis": 1,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 806,
              "total_time_in_millis": 145799,
              "total_docs": 2263195,
              "total_size_in_bytes": 2384482594,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 6482,
              "total_auto_throttle_in_bytes": 17331834
            },
            "refresh": {
              "total": 5013,
              "total_time_in_millis": 251386,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 43
            },
            "warmer": {
              "current": 0,
              "total": 5012,
              "total_time_in_millis": 2594
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 268,
              "hit_count": 22,
              "miss_count": 246,
              "cache_size": 0,
              "cache_count": 2,
              "evictions": 2
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 18,
              "memory_in_bytes": 945185,
              "terms_memory_in_bytes": 282994,
              "stored_fields_memory_in_bytes": 88360,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 44911,
              "doc_values_memory_in_bytes": 528920,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632834188,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195086852
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 12,
              "miss_count": 71
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4ArltMA==",
              "generation": 8,
              "user_data": {
                "local_checkpoint": "295410",
                "max_unsafe_auto_id_timestamp": "1542632834188",
                "translog_uuid": "Y2rEVkefTH2sQynPHxZF8Q",
                "history_uuid": "W8K4_wQmQTKCFXlQFenItg",
                "sync_id": "tOLA_jVUSaecDwapDkEhIQ",
                "translog_generation": "9",
                "max_seq_no": "295410"
              },
              "num_docs": 295411
            },
            "seq_no": {
              "max_seq_no": 295410,
              "local_checkpoint": 295410,
              "global_checkpoint": 295410
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "3": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 293767,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 206291804
            },
            "indexing": {
              "index_total": 288412,
              "index_time_in_millis": 119305,
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
              "query_total": 107,
              "query_time_in_millis": 2600,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 853,
              "total_time_in_millis": 146773,
              "total_docs": 2341580,
              "total_size_in_bytes": 2463177577,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 3644,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 5096,
              "total_time_in_millis": 257274,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 52
            },
            "warmer": {
              "current": 0,
              "total": 5094,
              "total_time_in_millis": 2401
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 310,
              "hit_count": 28,
              "miss_count": 282,
              "cache_size": 0,
              "cache_count": 2,
              "evictions": 2
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 14,
              "memory_in_bytes": 762104,
              "terms_memory_in_bytes": 233291,
              "stored_fields_memory_in_bytes": 87696,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 43701,
              "doc_values_memory_in_bytes": 397416,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632840947,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195085952
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 11,
              "miss_count": 71
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBh6sA==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "293766",
                "max_unsafe_auto_id_timestamp": "1542632840947",
                "translog_uuid": "a74k2eRvSfqCDP8MlgtJYg",
                "history_uuid": "TYCBIKQYQ-SXlTuu7N8Mvw",
                "sync_id": "gT0ssNmrR--ZUltgNzReuQ",
                "translog_generation": "9",
                "max_seq_no": "293766"
              },
              "num_docs": 293767
            },
            "seq_no": {
              "max_seq_no": 293766,
              "local_checkpoint": 293766,
              "global_checkpoint": 293766
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 293767,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 207700693
            },
            "indexing": {
              "index_total": 291423,
              "index_time_in_millis": 117265,
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
              "query_total": 105,
              "query_time_in_millis": 1193,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 889,
              "total_time_in_millis": 148829,
              "total_docs": 2204850,
              "total_size_in_bytes": 2382565183,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 2167,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 5145,
              "total_time_in_millis": 252431,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 92
            },
            "warmer": {
              "current": 0,
              "total": 5142,
              "total_time_in_millis": 2722
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 368,
              "hit_count": 24,
              "miss_count": 344,
              "cache_size": 0,
              "cache_count": 2,
              "evictions": 2
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 14,
              "memory_in_bytes": 952421,
              "terms_memory_in_bytes": 238683,
              "stored_fields_memory_in_bytes": 86848,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 44730,
              "doc_values_memory_in_bytes": 582160,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632130210,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195085965
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 14,
              "miss_count": 69
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 20
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWF7Miw==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "293766",
                "max_unsafe_auto_id_timestamp": "1542632130210",
                "translog_uuid": "o-0FUbZvQRCdVrdCwsPpcQ",
                "history_uuid": "TYCBIKQYQ-SXlTuu7N8Mvw",
                "sync_id": "gT0ssNmrR--ZUltgNzReuQ",
                "translog_generation": "13",
                "max_seq_no": "293766"
              },
              "num_docs": 293767
            },
            "seq_no": {
              "max_seq_no": 293766,
              "local_checkpoint": 293766,
              "global_checkpoint": 293766
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "4": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 294569,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 206705133
            },
            "indexing": {
              "index_total": 288923,
              "index_time_in_millis": 114426,
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
              "query_total": 102,
              "query_time_in_millis": 1555,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 796,
              "total_time_in_millis": 137757,
              "total_docs": 2244340,
              "total_size_in_bytes": 2354172060,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 4462,
              "total_auto_throttle_in_bytes": 17331834
            },
            "refresh": {
              "total": 5017,
              "total_time_in_millis": 221905,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 40
            },
            "warmer": {
              "current": 0,
              "total": 5015,
              "total_time_in_millis": 2271
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 334,
              "hit_count": 26,
              "miss_count": 308,
              "cache_size": 0,
              "cache_count": 2,
              "evictions": 2
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 11,
              "memory_in_bytes": 848344,
              "terms_memory_in_bytes": 201756,
              "stored_fields_memory_in_bytes": 84240,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 41944,
              "doc_values_memory_in_bytes": 520404,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632902546,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195086866
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 11,
              "miss_count": 72
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOgx2w==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "294568",
                "max_unsafe_auto_id_timestamp": "1542632902546",
                "translog_uuid": "1sjIe8OfQKyp5xWglsVKsQ",
                "history_uuid": "k_OjzAnbTj6E00-ThR6lTA",
                "sync_id": "BBGVv2jLRlurLPkUqOEOlg",
                "translog_generation": "9",
                "max_seq_no": "294568"
              },
              "num_docs": 294569
            },
            "seq_no": {
              "max_seq_no": 294568,
              "local_checkpoint": 294568,
              "global_checkpoint": 294568
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 294569,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 209284159
            },
            "indexing": {
              "index_total": 292288,
              "index_time_in_millis": 103121,
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
              "query_total": 110,
              "query_time_in_millis": 1460,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 795,
              "total_time_in_millis": 132941,
              "total_docs": 2206450,
              "total_size_in_bytes": 2324983673,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 3918,
              "total_auto_throttle_in_bytes": 17331834
            },
            "refresh": {
              "total": 5058,
              "total_time_in_millis": 225378,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 88
            },
            "warmer": {
              "current": 0,
              "total": 5055,
              "total_time_in_millis": 2771
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 457,
              "hit_count": 23,
              "miss_count": 434,
              "cache_size": 0,
              "cache_count": 2,
              "evictions": 2
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 18,
              "memory_in_bytes": 860134,
              "terms_memory_in_bytes": 284338,
              "stored_fields_memory_in_bytes": 86056,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 44452,
              "doc_values_memory_in_bytes": 445288,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632823649,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195086852
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 15,
              "miss_count": 67
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWF7Mgg==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "294568",
                "max_unsafe_auto_id_timestamp": "1542632823649",
                "translog_uuid": "Qda3obCqQnKdX4bEGoWL9A",
                "history_uuid": "k_OjzAnbTj6E00-ThR6lTA",
                "sync_id": "BBGVv2jLRlurLPkUqOEOlg",
                "translog_generation": "9",
                "max_seq_no": "294568"
              },
              "num_docs": 294569
            },
            "seq_no": {
              "max_seq_no": 294568,
              "local_checkpoint": 294568,
              "global_checkpoint": 294568
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-kibana-6-2018.11.19": {
      "uuid": "kT4EeXRhST6hEwHt18lOmw",
      "primaries": {
        "docs": {
          "count": 8640,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2965354
        },
        "indexing": {
          "index_total": 3987,
          "index_time_in_millis": 10065,
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
          "query_total": 435,
          "query_time_in_millis": 1196,
          "query_current": 0,
          "fetch_total": 1,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 439,
          "total_time_in_millis": 62219,
          "total_docs": 1463471,
          "total_size_in_bytes": 563064272,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 4392,
          "total_time_in_millis": 62720,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 27
        },
        "warmer": {
          "current": 0,
          "total": 4389,
          "total_time_in_millis": 156
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 7,
          "memory_in_bytes": 43296,
          "terms_memory_in_bytes": 32835,
          "stored_fields_memory_in_bytes": 2656,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 1465,
          "doc_values_memory_in_bytes": 6340,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542632816488,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 55,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 55,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 39,
          "miss_count": 363
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 9
        }
      },
      "total": {
        "docs": {
          "count": 17280,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 5819909
        },
        "indexing": {
          "index_total": 7951,
          "index_time_in_millis": 19185,
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
          "query_total": 860,
          "query_time_in_millis": 2316,
          "query_current": 0,
          "fetch_total": 1,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 877,
          "total_time_in_millis": 130339,
          "total_docs": 2927182,
          "total_size_in_bytes": 1107754516,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 8772,
          "total_time_in_millis": 121661,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 52
        },
        "warmer": {
          "current": 0,
          "total": 8767,
          "total_time_in_millis": 343
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 13,
          "memory_in_bytes": 81580,
          "terms_memory_in_bytes": 61073,
          "stored_fields_memory_in_bytes": 5024,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 2887,
          "doc_values_memory_in_bytes": 12596,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542632897332,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 110,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 77,
          "miss_count": 726
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 9
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 8640,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2854555
            },
            "indexing": {
              "index_total": 3964,
              "index_time_in_millis": 9120,
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
              "query_total": 425,
              "query_time_in_millis": 1120,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 438,
              "total_time_in_millis": 68120,
              "total_docs": 1463711,
              "total_size_in_bytes": 544690244,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 4380,
              "total_time_in_millis": 58941,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 25
            },
            "warmer": {
              "current": 0,
              "total": 4378,
              "total_time_in_millis": 187
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 6,
              "memory_in_bytes": 38284,
              "terms_memory_in_bytes": 28238,
              "stored_fields_memory_in_bytes": 2368,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1422,
              "doc_values_memory_in_bytes": 6256,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632897332,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195092113
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 38,
              "miss_count": 363
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOgxvw==",
              "generation": 8,
              "user_data": {
                "local_checkpoint": "8639",
                "max_unsafe_auto_id_timestamp": "1542632897332",
                "translog_uuid": "P4qeUVWPTwGsIQAJm8qpNg",
                "history_uuid": "qHj4h1M8RqW3AuqlynG4iA",
                "sync_id": "UlC7riE3RdWi9irtXKmIJA",
                "translog_generation": "3",
                "max_seq_no": "8639"
              },
              "num_docs": 8640
            },
            "seq_no": {
              "max_seq_no": 8639,
              "local_checkpoint": 8639,
              "global_checkpoint": 8639
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 8640,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 2965354
            },
            "indexing": {
              "index_total": 3987,
              "index_time_in_millis": 10065,
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
              "query_total": 435,
              "query_time_in_millis": 1196,
              "query_current": 0,
              "fetch_total": 1,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 439,
              "total_time_in_millis": 62219,
              "total_docs": 1463471,
              "total_size_in_bytes": 563064272,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 4392,
              "total_time_in_millis": 62720,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 27
            },
            "warmer": {
              "current": 0,
              "total": 4389,
              "total_time_in_millis": 156
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 7,
              "memory_in_bytes": 43296,
              "terms_memory_in_bytes": 32835,
              "stored_fields_memory_in_bytes": 2656,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 1465,
              "doc_values_memory_in_bytes": 6340,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542632816488,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 195091862
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 39,
              "miss_count": 363
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 9
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4ArltHw==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "8639",
                "max_unsafe_auto_id_timestamp": "1542632816488",
                "translog_uuid": "1BJ61FdtRzGLZSFqmg_c1g",
                "history_uuid": "qHj4h1M8RqW3AuqlynG4iA",
                "sync_id": "UlC7riE3RdWi9irtXKmIJA",
                "translog_generation": "10",
                "max_seq_no": "8639"
              },
              "num_docs": 8640
            },
            "seq_no": {
              "max_seq_no": 8639,
              "local_checkpoint": 8639,
              "global_checkpoint": 8639
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    "uuid2-6.5.0-2018.11.22": {
      "uuid": "9p4mj2ODQPSwGmOBk8ELZQ",
      "primaries": {
        "docs": {
          "count": 567644900,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 275824183094
        },
        "indexing": {
          "index_total": 567778255,
          "index_time_in_millis": 104896600,
          "index_current": 8,
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
          "query_total": 15510,
          "query_time_in_millis": 443205,
          "query_current": 0,
          "fetch_total": 1040,
          "fetch_time_in_millis": 8237,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 13,
          "current_docs": 42880229,
          "current_size_in_bytes": 17774716110,
          "total": 11881,
          "total_time_in_millis": 209902987,
          "total_docs": 1672412622,
          "total_size_in_bytes": 926424977318,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 151167527,
          "total_auto_throttle_in_bytes": 83886080
        },
        "refresh": {
          "total": 52887,
          "total_time_in_millis": 19196976,
          "listeners": 0
        },
        "flush": {
          "total": 1256,
          "periodic": 1252,
          "total_time_in_millis": 973126
        },
        "warmer": {
          "current": 0,
          "total": 51600,
          "total_time_in_millis": 2064
        },
        "query_cache": {
          "memory_size_in_bytes": 35763246,
          "total_count": 45464,
          "hit_count": 34006,
          "miss_count": 11458,
          "cache_size": 38,
          "cache_count": 41,
          "evictions": 3
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 641,
          "memory_in_bytes": 747183158,
          "terms_memory_in_bytes": 631042011,
          "stored_fields_memory_in_bytes": 103309408,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 12688647,
          "doc_values_memory_in_bytes": 143092,
          "index_writer_memory_in_bytes": 124352796,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542844802019,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 12506368,
          "size_in_bytes": 9543387699,
          "uncommitted_operations": 5121298,
          "uncommitted_size_in_bytes": 3908328086,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 567644900,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 275824183094
        },
        "indexing": {
          "index_total": 567778255,
          "index_time_in_millis": 104896600,
          "index_current": 8,
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
          "query_total": 15510,
          "query_time_in_millis": 443205,
          "query_current": 0,
          "fetch_total": 1040,
          "fetch_time_in_millis": 8237,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 13,
          "current_docs": 42880229,
          "current_size_in_bytes": 17774716110,
          "total": 11881,
          "total_time_in_millis": 209902987,
          "total_docs": 1672412622,
          "total_size_in_bytes": 926424977318,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 151167527,
          "total_auto_throttle_in_bytes": 83886080
        },
        "refresh": {
          "total": 52887,
          "total_time_in_millis": 19196976,
          "listeners": 0
        },
        "flush": {
          "total": 1256,
          "periodic": 1252,
          "total_time_in_millis": 973126
        },
        "warmer": {
          "current": 0,
          "total": 51600,
          "total_time_in_millis": 2064
        },
        "query_cache": {
          "memory_size_in_bytes": 35763246,
          "total_count": 45464,
          "hit_count": 34006,
          "miss_count": 11458,
          "cache_size": 38,
          "cache_count": 41,
          "evictions": 3
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 641,
          "memory_in_bytes": 747183158,
          "terms_memory_in_bytes": 631042011,
          "stored_fields_memory_in_bytes": 103309408,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 12688647,
          "doc_values_memory_in_bytes": 143092,
          "index_writer_memory_in_bytes": 124352796,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542844802019,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 12506368,
          "size_in_bytes": 9543387699,
          "uncommitted_operations": 5121298,
          "uncommitted_size_in_bytes": 3908328086,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 34600152,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 18954800033
            },
            "indexing": {
              "index_total": 34601945,
              "index_time_in_millis": 6153825,
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
              "query_total": 951,
              "query_time_in_millis": 15433,
              "query_current": 0,
              "fetch_total": 6,
              "fetch_time_in_millis": 266,
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
              "current_docs": 12224086,
              "current_size_in_bytes": 5638166097,
              "total": 755,
              "total_time_in_millis": 12519344,
              "total_docs": 103727394,
              "total_size_in_bytes": 57587109266,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 8909858,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3266,
              "total_time_in_millis": 1081735,
              "listeners": 0
            },
            "flush": {
              "total": 77,
              "periodic": 76,
              "total_time_in_millis": 56845
            },
            "warmer": {
              "current": 0,
              "total": 3186,
              "total_time_in_millis": 105
            },
            "query_cache": {
              "memory_size_in_bytes": 2560388,
              "total_count": 1932,
              "hit_count": 1751,
              "miss_count": 181,
              "cache_size": 2,
              "cache_count": 2,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 49,
              "memory_in_bytes": 45771281,
              "terms_memory_in_bytes": 38656518,
              "stored_fields_memory_in_bytes": 6327752,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 775871,
              "doc_values_memory_in_bytes": 11140,
              "index_writer_memory_in_bytes": 2454276,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 810618,
              "size_in_bytes": 618534302,
              "uncommitted_operations": 283115,
              "uncommitted_size_in_bytes": 215972102,
              "earliest_last_modified_age": 316401
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO/qYQ==",
              "generation": 80,
              "user_data": {
                "local_checkpoint": "34318829",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "D7kHQGuZRziZf4Ua6SqewA",
                "history_uuid": "UvooZjRbTf6_-Jvnra1tJQ",
                "translog_generation": "608",
                "max_seq_no": "34319528"
              },
              "num_docs": 34318832
            },
            "seq_no": {
              "max_seq_no": 34601944,
              "local_checkpoint": 34601944,
              "global_checkpoint": 34601944
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "1": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 35853546,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 17011795108
            },
            "indexing": {
              "index_total": 35861766,
              "index_time_in_millis": 6760866,
              "index_current": 1,
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
              "query_total": 976,
              "query_time_in_millis": 34522,
              "query_current": 0,
              "fetch_total": 11,
              "fetch_time_in_millis": 527,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 1,
              "current_docs": 747356,
              "current_size_in_bytes": 288376265,
              "total": 781,
              "total_time_in_millis": 13471849,
              "total_docs": 106636862,
              "total_size_in_bytes": 59054354256,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9599161,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3303,
              "total_time_in_millis": 1247650,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 62449
            },
            "warmer": {
              "current": 0,
              "total": 3223,
              "total_time_in_millis": 134
            },
            "query_cache": {
              "memory_size_in_bytes": 2748512,
              "total_count": 3471,
              "hit_count": 2618,
              "miss_count": 853,
              "cache_size": 3,
              "cache_count": 3,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 47,
              "memory_in_bytes": 46683746,
              "terms_memory_in_bytes": 39310616,
              "stored_fields_memory_in_bytes": 6559280,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 802014,
              "doc_values_memory_in_bytes": 11836,
              "index_writer_memory_in_bytes": 8874420,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 770267,
              "size_in_bytes": 587830147,
              "uncommitted_operations": 683063,
              "uncommitted_size_in_bytes": 521372242,
              "earliest_last_modified_age": 301944
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsEHVg==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35178721",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "YLbeFshaQlqx7L8eCJdMwg",
                "history_uuid": "25KmNEMySz6VHGXqktWMZg",
                "translog_generation": "627",
                "max_seq_no": "35178724"
              },
              "num_docs": 35178723
            },
            "seq_no": {
              "max_seq_no": 35861766,
              "local_checkpoint": 35861765,
              "global_checkpoint": 35861518
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "2": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 35829463,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 17382687594
            },
            "indexing": {
              "index_total": 35832469,
              "index_time_in_millis": 6769429,
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
              "query_total": 976,
              "query_time_in_millis": 30876,
              "query_current": 0,
              "fetch_total": 6,
              "fetch_time_in_millis": 793,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 1,
              "current_docs": 917452,
              "current_size_in_bytes": 353090636,
              "total": 807,
              "total_time_in_millis": 12538523,
              "total_docs": 101372099,
              "total_size_in_bytes": 56451599696,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 8967648,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3366,
              "total_time_in_millis": 1142295,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 64359
            },
            "warmer": {
              "current": 0,
              "total": 3286,
              "total_time_in_millis": 167
            },
            "query_cache": {
              "memory_size_in_bytes": 2191812,
              "total_count": 1749,
              "hit_count": 864,
              "miss_count": 885,
              "cache_size": 3,
              "cache_count": 3,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 48,
              "memory_in_bytes": 50837896,
              "terms_memory_in_bytes": 43450316,
              "stored_fields_memory_in_bytes": 6571104,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 801476,
              "doc_values_memory_in_bytes": 15000,
              "index_writer_memory_in_bytes": 3377080,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 734631,
              "size_in_bytes": 560582716,
              "uncommitted_operations": 30953,
              "uncommitted_size_in_bytes": 23570158,
              "earliest_last_modified_age": 289491
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGdMUQ==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35801515",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "EMt3WBjPSZ-uiH4T50Wdqg",
                "history_uuid": "L9f26HlxTl-R7lG3j--s9g",
                "translog_generation": "634",
                "max_seq_no": "35801786"
              },
              "num_docs": 35801516
            },
            "seq_no": {
              "max_seq_no": 35832468,
              "local_checkpoint": 35832468,
              "global_checkpoint": 35832212
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "3": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 35851263,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 18178159477
            },
            "indexing": {
              "index_total": 35859338,
              "index_time_in_millis": 6900471,
              "index_current": 1,
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
              "query_total": 976,
              "query_time_in_millis": 29809,
              "query_current": 0,
              "fetch_total": 7,
              "fetch_time_in_millis": 844,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 1,
              "current_docs": 6224543,
              "current_size_in_bytes": 2644891734,
              "total": 786,
              "total_time_in_millis": 13534220,
              "total_docs": 109193344,
              "total_size_in_bytes": 60585072401,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9622109,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3319,
              "total_time_in_millis": 1227537,
              "listeners": 0
            },
            "flush": {
              "total": 80,
              "periodic": 80,
              "total_time_in_millis": 64324
            },
            "warmer": {
              "current": 0,
              "total": 3238,
              "total_time_in_millis": 131
            },
            "query_cache": {
              "memory_size_in_bytes": 2024093,
              "total_count": 3286,
              "hit_count": 2577,
              "miss_count": 709,
              "cache_size": 2,
              "cache_count": 3,
              "evictions": 1
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 44,
              "memory_in_bytes": 46595386,
              "terms_memory_in_bytes": 39221352,
              "stored_fields_memory_in_bytes": 6562240,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 802658,
              "doc_values_memory_in_bytes": 9136,
              "index_writer_memory_in_bytes": 8764956,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 770372,
              "size_in_bytes": 587858885,
              "uncommitted_operations": 66892,
              "uncommitted_size_in_bytes": 50975450,
              "earliest_last_modified_age": 302344
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB9/iQ==",
              "generation": 82,
              "user_data": {
                "local_checkpoint": "35792455",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "zeqThyrhRn6bfR0Wp-TJrQ",
                "history_uuid": "oq0Bt-BpTMO2r13WY35rJQ",
                "translog_generation": "635",
                "max_seq_no": "35792455"
              },
              "num_docs": 35792456
            },
            "seq_no": {
              "max_seq_no": 35859338,
              "local_checkpoint": 35859337,
              "global_checkpoint": 35859143
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "4": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 34435704,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 16351285157
            },
            "indexing": {
              "index_total": 34455927,
              "index_time_in_millis": 6153425,
              "index_current": 1,
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
              "query_total": 949,
              "query_time_in_millis": 14939,
              "query_current": 0,
              "fetch_total": 2,
              "fetch_time_in_millis": 70,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 1,
              "current_docs": 4246768,
              "current_size_in_bytes": 1625279608,
              "total": 714,
              "total_time_in_millis": 11714500,
              "total_docs": 93102531,
              "total_size_in_bytes": 52129778451,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 8482093,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3265,
              "total_time_in_millis": 1094908,
              "listeners": 0
            },
            "flush": {
              "total": 77,
              "periodic": 76,
              "total_time_in_millis": 56871
            },
            "warmer": {
              "current": 0,
              "total": 3186,
              "total_time_in_millis": 109
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 419,
              "hit_count": 0,
              "miss_count": 419,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 42,
              "memory_in_bytes": 53435294,
              "terms_memory_in_bytes": 46373956,
              "stored_fields_memory_in_bytes": 6276304,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 772378,
              "doc_values_memory_in_bytes": 12656,
              "index_writer_memory_in_bytes": 8780972,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 735680,
              "size_in_bytes": 561419458,
              "uncommitted_operations": 208040,
              "uncommitted_size_in_bytes": 158691876,
              "earliest_last_modified_age": 289434
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO/qqQ==",
              "generation": 80,
              "user_data": {
                "local_checkpoint": "34247886",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "FS-B_N13S1-qYEen5YTcdg",
                "history_uuid": "ik0kSVOxRIWiOLc7jSHZ0w",
                "translog_generation": "608",
                "max_seq_no": "34248595"
              },
              "num_docs": 34247888
            },
            "seq_no": {
              "max_seq_no": 34455927,
              "local_checkpoint": 34455437,
              "global_checkpoint": 34455437
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "5": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 35866650,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 16865320524
            },
            "indexing": {
              "index_total": 35873056,
              "index_time_in_millis": 6776463,
              "index_current": 1,
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
              "query_total": 976,
              "query_time_in_millis": 35212,
              "query_current": 0,
              "fetch_total": 18,
              "fetch_time_in_millis": 476,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 748,
              "total_time_in_millis": 13561825,
              "total_docs": 106881449,
              "total_size_in_bytes": 59294093248,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9744328,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3267,
              "total_time_in_millis": 1282316,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 64912
            },
            "warmer": {
              "current": 0,
              "total": 3186,
              "total_time_in_millis": 125
            },
            "query_cache": {
              "memory_size_in_bytes": 2769536,
              "total_count": 3609,
              "hit_count": 2649,
              "miss_count": 960,
              "cache_size": 3,
              "cache_count": 3,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 30,
              "memory_in_bytes": 44981880,
              "terms_memory_in_bytes": 37642788,
              "stored_fields_memory_in_bytes": 6532880,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 800332,
              "doc_values_memory_in_bytes": 5880,
              "index_writer_memory_in_bytes": 7271736,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 795463,
              "size_in_bytes": 607026240,
              "uncommitted_operations": 355702,
              "uncommitted_size_in_bytes": 271502470,
              "earliest_last_modified_age": 310671
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsEJFg==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35517369",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "kO8EzoFDR-mC2Hl_xbX9AQ",
                "history_uuid": "pO-kV20yRPWDoft_F4W9Fw",
                "translog_generation": "631",
                "max_seq_no": "35517370"
              },
              "num_docs": 35517370
            },
            "seq_no": {
              "max_seq_no": 35873056,
              "local_checkpoint": 35873055,
              "global_checkpoint": 35872893
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "6": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 35816085,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 17836707748
            },
            "indexing": {
              "index_total": 35818130,
              "index_time_in_millis": 6798477,
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
              "query_total": 976,
              "query_time_in_millis": 31666,
              "query_current": 0,
              "fetch_total": 5,
              "fetch_time_in_millis": 570,
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
              "current_docs": 5876085,
              "current_size_in_bytes": 2268814561,
              "total": 765,
              "total_time_in_millis": 12861994,
              "total_docs": 104194846,
              "total_size_in_bytes": 58089253564,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9149554,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3353,
              "total_time_in_millis": 1165244,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 62758
            },
            "warmer": {
              "current": 0,
              "total": 3273,
              "total_time_in_millis": 153
            },
            "query_cache": {
              "memory_size_in_bytes": 2827796,
              "total_count": 3300,
              "hit_count": 2620,
              "miss_count": 680,
              "cache_size": 3,
              "cache_count": 3,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 47,
              "memory_in_bytes": 47344152,
              "terms_memory_in_bytes": 39985693,
              "stored_fields_memory_in_bytes": 6545824,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 801199,
              "doc_values_memory_in_bytes": 11436,
              "index_writer_memory_in_bytes": 3453352,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 704222,
              "size_in_bytes": 537451914,
              "uncommitted_operations": 616819,
              "uncommitted_size_in_bytes": 470907012,
              "earliest_last_modified_age": 276231
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGdJmQ==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35201310",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "VDi3jzH_SZKeA_may6sXFw",
                "history_uuid": "js20NxfyR0-V2USe3EABrQ",
                "translog_generation": "626",
                "max_seq_no": "35201310"
              },
              "num_docs": 35201311
            },
            "seq_no": {
              "max_seq_no": 35818129,
              "local_checkpoint": 35818129,
              "global_checkpoint": 35818129
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "7": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 35853562,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 16586285299
            },
            "indexing": {
              "index_total": 35860350,
              "index_time_in_millis": 6946387,
              "index_current": 1,
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
              "query_total": 976,
              "query_time_in_millis": 31308,
              "query_current": 0,
              "fetch_total": 9,
              "fetch_time_in_millis": 901,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 753,
              "total_time_in_millis": 13867040,
              "total_docs": 113725166,
              "total_size_in_bytes": 62211427380,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9981237,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3318,
              "total_time_in_millis": 1256419,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 62955
            },
            "warmer": {
              "current": 0,
              "total": 3236,
              "total_time_in_millis": 128
            },
            "query_cache": {
              "memory_size_in_bytes": 2039557,
              "total_count": 3457,
              "hit_count": 2596,
              "miss_count": 861,
              "cache_size": 2,
              "cache_count": 3,
              "evictions": 1
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 28,
              "memory_in_bytes": 40189254,
              "terms_memory_in_bytes": 32837860,
              "stored_fields_memory_in_bytes": 6547176,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 798114,
              "doc_values_memory_in_bytes": 6104,
              "index_writer_memory_in_bytes": 7842968,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 780990,
              "size_in_bytes": 595945505,
              "uncommitted_operations": 165489,
              "uncommitted_size_in_bytes": 126224137,
              "earliest_last_modified_age": 305656
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB9/KA==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35694869",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "ijJqnwHrSBqR5WDaombd5A",
                "history_uuid": "jzgqYDXRTVCLt_WIe3j2zQ",
                "translog_generation": "632",
                "max_seq_no": "35695310"
              },
              "num_docs": 35694871
            },
            "seq_no": {
              "max_seq_no": 35860350,
              "local_checkpoint": 35860349,
              "global_checkpoint": 35860213
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "8": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 34316169,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 15827784796
            },
            "indexing": {
              "index_total": 34319000,
              "index_time_in_millis": 6073777,
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
              "query_total": 949,
              "query_time_in_millis": 16657,
              "query_current": 0,
              "fetch_total": 2,
              "fetch_time_in_millis": 92,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 1,
              "current_docs": 5689364,
              "current_size_in_bytes": 2188255780,
              "total": 695,
              "total_time_in_millis": 12723646,
              "total_docs": 105996216,
              "total_size_in_bytes": 58483230333,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9114570,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3256,
              "total_time_in_millis": 1070483,
              "listeners": 0
            },
            "flush": {
              "total": 76,
              "periodic": 75,
              "total_time_in_millis": 54926
            },
            "warmer": {
              "current": 0,
              "total": 3178,
              "total_time_in_millis": 118
            },
            "query_cache": {
              "memory_size_in_bytes": 2057476,
              "total_count": 2063,
              "hit_count": 1773,
              "miss_count": 290,
              "cache_size": 2,
              "cache_count": 2,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 43,
              "memory_in_bytes": 40426982,
              "terms_memory_in_bytes": 33403836,
              "stored_fields_memory_in_bytes": 6249344,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 766222,
              "doc_values_memory_in_bytes": 7580,
              "index_writer_memory_in_bytes": 4107096,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 820469,
              "size_in_bytes": 626052288,
              "uncommitted_operations": 204996,
              "uncommitted_size_in_bytes": 156361945,
              "earliest_last_modified_age": 319152
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO/qtA==",
              "generation": 79,
              "user_data": {
                "local_checkpoint": "34114003",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "d3iJi3nETduHzkoxA6yt4g",
                "history_uuid": "52eCAqGMQXSLPENS_bAK8A",
                "translog_generation": "605",
                "max_seq_no": "34114283"
              },
              "num_docs": 34114004
            },
            "seq_no": {
              "max_seq_no": 34318999,
              "local_checkpoint": 34318999,
              "global_checkpoint": 34318999
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "9": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 35859915,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 18756879108
            },
            "indexing": {
              "index_total": 35869078,
              "index_time_in_millis": 6642642,
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
              "query_total": 976,
              "query_time_in_millis": 36462,
              "query_current": 0,
              "fetch_total": 15,
              "fetch_time_in_millis": 611,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 1,
              "current_docs": 953690,
              "current_size_in_bytes": 367434027,
              "total": 713,
              "total_time_in_millis": 14221438,
              "total_docs": 113160583,
              "total_size_in_bytes": 61924340845,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 10222015,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3299,
              "total_time_in_millis": 1251971,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 64715
            },
            "warmer": {
              "current": 0,
              "total": 3218,
              "total_time_in_millis": 134
            },
            "query_cache": {
              "memory_size_in_bytes": 2082838,
              "total_count": 3343,
              "hit_count": 2633,
              "miss_count": 710,
              "cache_size": 2,
              "cache_count": 3,
              "evictions": 1
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 39,
              "memory_in_bytes": 39813068,
              "terms_memory_in_bytes": 32469735,
              "stored_fields_memory_in_bytes": 6535800,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 799265,
              "doc_values_memory_in_bytes": 8268,
              "index_writer_memory_in_bytes": 10870732,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 792326,
              "size_in_bytes": 604578230,
              "uncommitted_operations": 439941,
              "uncommitted_size_in_bytes": 335918180,
              "earliest_last_modified_age": 309675
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsEIqw==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35429136",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "ABIz6znyQOKwGhP9eHn6Xw",
                "history_uuid": "XpwYmm4eQf6L-EtbSasuVQ",
                "translog_generation": "632",
                "max_seq_no": "35429138"
              },
              "num_docs": 35429138
            },
            "seq_no": {
              "max_seq_no": 35869077,
              "local_checkpoint": 35869077,
              "global_checkpoint": 35868834
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "10": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 35808935,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 16986600511
            },
            "indexing": {
              "index_total": 35812681,
              "index_time_in_millis": 6714959,
              "index_current": 1,
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
              "query_total": 975,
              "query_time_in_millis": 32363,
              "query_current": 0,
              "fetch_total": 922,
              "fetch_time_in_millis": 701,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 1,
              "current_docs": 783808,
              "current_size_in_bytes": 301863727,
              "total": 735,
              "total_time_in_millis": 13518918,
              "total_docs": 108555271,
              "total_size_in_bytes": 60217245048,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9691764,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3364,
              "total_time_in_millis": 1145753,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 60387
            },
            "warmer": {
              "current": 0,
              "total": 3282,
              "total_time_in_millis": 132
            },
            "query_cache": {
              "memory_size_in_bytes": 2583280,
              "total_count": 2332,
              "hit_count": 1750,
              "miss_count": 582,
              "cache_size": 2,
              "cache_count": 2,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 41,
              "memory_in_bytes": 44851695,
              "terms_memory_in_bytes": 37500356,
              "stored_fields_memory_in_bytes": 6543408,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 801247,
              "doc_values_memory_in_bytes": 6684,
              "index_writer_memory_in_bytes": 4866092,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 867283,
              "size_in_bytes": 661772853,
              "uncommitted_operations": 692061,
              "uncommitted_size_in_bytes": 528199460,
              "earliest_last_modified_age": 348923
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGdJRQ==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35120628",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "UwK9mvX-QpaoYOOagYQMuA",
                "history_uuid": "6zAuOAOcROi5MDPR72vtcQ",
                "translog_generation": "628",
                "max_seq_no": "35120953"
              },
              "num_docs": 35120630
            },
            "seq_no": {
              "max_seq_no": 35812681,
              "local_checkpoint": 35812680,
              "global_checkpoint": 35812486
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "11": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 35850165,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 16762504455
            },
            "indexing": {
              "index_total": 35859569,
              "index_time_in_millis": 6769397,
              "index_current": 1,
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
              "query_total": 976,
              "query_time_in_millis": 29322,
              "query_current": 0,
              "fetch_total": 6,
              "fetch_time_in_millis": 526,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 1,
              "current_docs": 784387,
              "current_size_in_bytes": 302368880,
              "total": 731,
              "total_time_in_millis": 13551347,
              "total_docs": 106739948,
              "total_size_in_bytes": 58923999244,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9766383,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3325,
              "total_time_in_millis": 1244694,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 62274
            },
            "warmer": {
              "current": 0,
              "total": 3244,
              "total_time_in_millis": 132
            },
            "query_cache": {
              "memory_size_in_bytes": 2830263,
              "total_count": 3355,
              "hit_count": 2600,
              "miss_count": 755,
              "cache_size": 3,
              "cache_count": 3,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 39,
              "memory_in_bytes": 44675397,
              "terms_memory_in_bytes": 37344381,
              "stored_fields_memory_in_bytes": 6523576,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 800580,
              "doc_values_memory_in_bytes": 6860,
              "index_writer_memory_in_bytes": 9706996,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 774454,
              "size_in_bytes": 590996021,
              "uncommitted_operations": 334913,
              "uncommitted_size_in_bytes": 255610814,
              "earliest_last_modified_age": 303143
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB9+Sg==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35524666",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "TVbKsahhSEGiK4O3_XF2VA",
                "history_uuid": "l4Kue3LaSJWgOoucgQvBMQ",
                "translog_generation": "631",
                "max_seq_no": "35524666"
              },
              "num_docs": 35524667
            },
            "seq_no": {
              "max_seq_no": 35859569,
              "local_checkpoint": 35859568,
              "global_checkpoint": 35859409
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "12": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 34206226,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 16193411482
            },
            "indexing": {
              "index_total": 34225501,
              "index_time_in_millis": 5842829,
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
              "query_total": 950,
              "query_time_in_millis": 11328,
              "query_current": 0,
              "fetch_total": 2,
              "fetch_time_in_millis": 84,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 696,
              "total_time_in_millis": 11846071,
              "total_docs": 93119591,
              "total_size_in_bytes": 51943636740,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 8691984,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3250,
              "total_time_in_millis": 1125437,
              "listeners": 0
            },
            "flush": {
              "total": 76,
              "periodic": 75,
              "total_time_in_millis": 59776
            },
            "warmer": {
              "current": 0,
              "total": 3171,
              "total_time_in_millis": 111
            },
            "query_cache": {
              "memory_size_in_bytes": 1439916,
              "total_count": 2134,
              "hit_count": 1765,
              "miss_count": 369,
              "cache_size": 2,
              "cache_count": 2,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 33,
              "memory_in_bytes": 51736310,
              "terms_memory_in_bytes": 44811861,
              "stored_fields_memory_in_bytes": 6152624,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 766053,
              "doc_values_memory_in_bytes": 5772,
              "index_writer_memory_in_bytes": 18168868,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 737182,
              "size_in_bytes": 562560864,
              "uncommitted_operations": 209719,
              "uncommitted_size_in_bytes": 159956900,
              "earliest_last_modified_age": 289692
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO/qog==",
              "generation": 79,
              "user_data": {
                "local_checkpoint": "34015781",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "pjv-FnCyQsmlN1q7uEfNXw",
                "history_uuid": "oRrIqXt8Qm-EAAWJlNf0_w",
                "translog_generation": "602",
                "max_seq_no": "34016261"
              },
              "num_docs": 34015782
            },
            "seq_no": {
              "max_seq_no": 34225500,
              "local_checkpoint": 34225500,
              "global_checkpoint": 34225500
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "13": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 35857376,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 16726386494
            },
            "indexing": {
              "index_total": 35864504,
              "index_time_in_millis": 6429789,
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
              "query_total": 976,
              "query_time_in_millis": 37442,
              "query_current": 0,
              "fetch_total": 11,
              "fetch_time_in_millis": 470,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 724,
              "total_time_in_millis": 13555352,
              "total_docs": 103527843,
              "total_size_in_bytes": 57135067295,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9901261,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3293,
              "total_time_in_millis": 1332657,
              "listeners": 0
            },
            "flush": {
              "total": 80,
              "periodic": 80,
              "total_time_in_millis": 62386
            },
            "warmer": {
              "current": 0,
              "total": 3212,
              "total_time_in_millis": 122
            },
            "query_cache": {
              "memory_size_in_bytes": 2394040,
              "total_count": 3637,
              "hit_count": 2573,
              "miss_count": 1064,
              "cache_size": 3,
              "cache_count": 3,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 35,
              "memory_in_bytes": 45257134,
              "terms_memory_in_bytes": 38001868,
              "stored_fields_memory_in_bytes": 6448216,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 798742,
              "doc_values_memory_in_bytes": 8308,
              "index_writer_memory_in_bytes": 7920824,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 775276,
              "size_in_bytes": 591583677,
              "uncommitted_operations": 159733,
              "uncommitted_size_in_bytes": 121808284,
              "earliest_last_modified_age": 303613
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsEKNg==",
              "generation": 82,
              "user_data": {
                "local_checkpoint": "35704770",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "WGedbaXeSZ-50XmTpZzlSQ",
                "history_uuid": "zxqw-uwLS4WFA8F1Dbu5aQ",
                "translog_generation": "638",
                "max_seq_no": "35705307"
              },
              "num_docs": 35704771
            },
            "seq_no": {
              "max_seq_no": 35864503,
              "local_checkpoint": 35864503,
              "global_checkpoint": 35864213
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "14": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 35792158,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 18461502541
            },
            "indexing": {
              "index_total": 35811995,
              "index_time_in_millis": 6460244,
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
              "query_total": 976,
              "query_time_in_millis": 31225,
              "query_current": 0,
              "fetch_total": 8,
              "fetch_time_in_millis": 656,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 1,
              "current_docs": 4432690,
              "current_size_in_bytes": 1796174795,
              "total": 740,
              "total_time_in_millis": 13313304,
              "total_docs": 101396765,
              "total_size_in_bytes": 56448356543,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9720866,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3340,
              "total_time_in_millis": 1229531,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 55557
            },
            "warmer": {
              "current": 0,
              "total": 3260,
              "total_time_in_millis": 136
            },
            "query_cache": {
              "memory_size_in_bytes": 2928588,
              "total_count": 3563,
              "hit_count": 2644,
              "miss_count": 919,
              "cache_size": 3,
              "cache_count": 3,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 42,
              "memory_in_bytes": 53118126,
              "terms_memory_in_bytes": 45862415,
              "stored_fields_memory_in_bytes": 6443408,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 802415,
              "doc_values_memory_in_bytes": 9888,
              "index_writer_memory_in_bytes": 12212488,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844802019,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 873624,
              "size_in_bytes": 666570478,
              "uncommitted_operations": 345952,
              "uncommitted_size_in_bytes": 264074692,
              "earliest_last_modified_age": 351482
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGdKxQ==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35466049",
                "max_unsafe_auto_id_timestamp": "1542844802019",
                "translog_uuid": "w4-S5_izRvKcVj1XhkSrxg",
                "history_uuid": "MUnHLsXeS4mtAsDlQPQ-pA",
                "translog_generation": "630",
                "max_seq_no": "35466848"
              },
              "num_docs": 35466051
            },
            "seq_no": {
              "max_seq_no": 35811994,
              "local_checkpoint": 35811994,
              "global_checkpoint": 35811119
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "15": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 35847531,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 16942072767
            },
            "indexing": {
              "index_total": 35852946,
              "index_time_in_millis": 6703620,
              "index_current": 1,
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
              "query_total": 976,
              "query_time_in_millis": 24641,
              "query_current": 0,
              "fetch_total": 10,
              "fetch_time_in_millis": 650,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 738,
              "total_time_in_millis": 13103616,
              "total_docs": 101082714,
              "total_size_in_bytes": 55946413008,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 9602696,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 3303,
              "total_time_in_millis": 1298346,
              "listeners": 0
            },
            "flush": {
              "total": 79,
              "periodic": 79,
              "total_time_in_millis": 57632
            },
            "warmer": {
              "current": 0,
              "total": 3221,
              "total_time_in_millis": 127
            },
            "query_cache": {
              "memory_size_in_bytes": 2285151,
              "total_count": 3814,
              "hit_count": 2593,
              "miss_count": 1221,
              "cache_size": 3,
              "cache_count": 3,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 34,
              "memory_in_bytes": 51465557,
              "terms_memory_in_bytes": 44168460,
              "stored_fields_memory_in_bytes": 6490472,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 800081,
              "doc_values_memory_in_bytes": 6544,
              "index_writer_memory_in_bytes": 5679940,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844801872,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 763511,
              "size_in_bytes": 582624121,
              "uncommitted_operations": 323910,
              "uncommitted_size_in_bytes": 247182364,
              "earliest_last_modified_age": 300145
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB9+bg==",
              "generation": 81,
              "user_data": {
                "local_checkpoint": "35529045",
                "max_unsafe_auto_id_timestamp": "1542844801872",
                "translog_uuid": "gW0k28YFSQuJvBBmKdM2tA",
                "history_uuid": "E83oJ1VHSDaomR5nL_t26g",
                "translog_generation": "632",
                "max_seq_no": "35529045"
              },
              "num_docs": 35529046
            },
            "seq_no": {
              "max_seq_no": 35852946,
              "local_checkpoint": 35852945,
              "global_checkpoint": 35852780
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".kibana_2": {
      "uuid": "mjNxlmDDSaGA86fU655ppg",
      "primaries": {
        "docs": {
          "count": 9,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 69069
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "total": 23457,
          "time_in_millis": 1848,
          "exists_total": 11897,
          "exists_time_in_millis": 1040,
          "missing_total": 11560,
          "missing_time_in_millis": 808,
          "current": 0
        },
        "search": {
          "open_contexts": 0,
          "query_total": 82115,
          "query_time_in_millis": 8740,
          "query_current": 0,
          "fetch_total": 82096,
          "fetch_time_in_millis": 2510,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 5,
          "total_time_in_millis": 4,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 2,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 920,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 8,
          "memory_in_bytes": 17094,
          "terms_memory_in_bytes": 12822,
          "stored_fields_memory_in_bytes": 2496,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 1216,
          "points_memory_in_bytes": 16,
          "doc_values_memory_in_bytes": 544,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 7,
          "size_in_bytes": 48329,
          "uncommitted_operations": 7,
          "uncommitted_size_in_bytes": 48329,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 848,
          "evictions": 0,
          "hit_count": 11736,
          "miss_count": 5
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 18,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 138138
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "total": 47181,
          "time_in_millis": 3886,
          "exists_total": 23724,
          "exists_time_in_millis": 2041,
          "missing_total": 23457,
          "missing_time_in_millis": 1845,
          "current": 0
        },
        "search": {
          "open_contexts": 0,
          "query_total": 164410,
          "query_time_in_millis": 18714,
          "query_current": 0,
          "fetch_total": 164365,
          "fetch_time_in_millis": 5051,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 10,
          "total_time_in_millis": 5,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 4,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 1840,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 16,
          "memory_in_bytes": 34188,
          "terms_memory_in_bytes": 25644,
          "stored_fields_memory_in_bytes": 4992,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 2432,
          "points_memory_in_bytes": 32,
          "doc_values_memory_in_bytes": 1088,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 14,
          "size_in_bytes": 96658,
          "uncommitted_operations": 14,
          "uncommitted_size_in_bytes": 96658,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 1696,
          "evictions": 0,
          "hit_count": 23451,
          "miss_count": 8
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 9,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 69069
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "total": 23457,
              "time_in_millis": 1848,
              "exists_total": 11897,
              "exists_time_in_millis": 1040,
              "missing_total": 11560,
              "missing_time_in_millis": 808,
              "current": 0
            },
            "search": {
              "open_contexts": 0,
              "query_total": 82115,
              "query_time_in_millis": 8740,
              "query_current": 0,
              "fetch_total": 82096,
              "fetch_time_in_millis": 2510,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 5,
              "total_time_in_millis": 4,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 2,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 920,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 8,
              "memory_in_bytes": 17094,
              "terms_memory_in_bytes": 12822,
              "stored_fields_memory_in_bytes": 2496,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 1216,
              "points_memory_in_bytes": 16,
              "doc_values_memory_in_bytes": 544,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 7,
              "size_in_bytes": 48329,
              "uncommitted_operations": 7,
              "uncommitted_size_in_bytes": 48329,
              "earliest_last_modified_age": 234478006
            },
            "request_cache": {
              "memory_size_in_bytes": 848,
              "evictions": 0,
              "hit_count": 11736,
              "miss_count": 5
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbObjaw==",
              "generation": 20,
              "user_data": {
                "local_checkpoint": "16",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "LfG5sgynT8SrGPW71Ilz9Q",
                "history_uuid": "I31ODraXQg-dhxgaGUbKQg",
                "sync_id": "Rn4W1L_yS8eGm-eVuy9lVA",
                "translog_generation": "2",
                "max_seq_no": "16"
              },
              "num_docs": 9
            },
            "seq_no": {
              "max_seq_no": 16,
              "local_checkpoint": 16,
              "global_checkpoint": 16
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 9,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 69069
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "total": 23724,
              "time_in_millis": 2038,
              "exists_total": 11827,
              "exists_time_in_millis": 1001,
              "missing_total": 11897,
              "missing_time_in_millis": 1037,
              "current": 0
            },
            "search": {
              "open_contexts": 0,
              "query_total": 82295,
              "query_time_in_millis": 9974,
              "query_current": 0,
              "fetch_total": 82269,
              "fetch_time_in_millis": 2541,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 5,
              "total_time_in_millis": 1,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 2,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 920,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 8,
              "memory_in_bytes": 17094,
              "terms_memory_in_bytes": 12822,
              "stored_fields_memory_in_bytes": 2496,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 1216,
              "points_memory_in_bytes": 16,
              "doc_values_memory_in_bytes": 544,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 7,
              "size_in_bytes": 48329,
              "uncommitted_operations": 7,
              "uncommitted_size_in_bytes": 48329,
              "earliest_last_modified_age": 234540858
            },
            "request_cache": {
              "memory_size_in_bytes": 848,
              "evictions": 0,
              "hit_count": 11715,
              "miss_count": 3
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBbdJQ==",
              "generation": 20,
              "user_data": {
                "local_checkpoint": "16",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "5m12Ni6IQHa2lmsjZ8CjNw",
                "history_uuid": "I31ODraXQg-dhxgaGUbKQg",
                "sync_id": "Rn4W1L_yS8eGm-eVuy9lVA",
                "translog_generation": "2",
                "max_seq_no": "16"
              },
              "num_docs": 9
            },
            "seq_no": {
              "max_seq_no": 16,
              "local_checkpoint": 16,
              "global_checkpoint": 16
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    "uuid2-6.5.0-2018.11.21": {
      "uuid": "hO5l72DeTo-uyKpm4gHkKA",
      "primaries": {
        "docs": {
          "count": 2396729464,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 1156970597395
        },
        "indexing": {
          "index_total": 2396729464,
          "index_time_in_millis": 470876005,
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
          "query_total": 72063,
          "query_time_in_millis": 6961193,
          "query_current": 0,
          "fetch_total": 2655,
          "fetch_time_in_millis": 1773,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 46461,
          "total_time_in_millis": 1239514679,
          "total_docs": 7391380284,
          "total_size_in_bytes": 4267605661181,
          "total_stopped_time_in_millis": 16562,
          "total_throttled_time_in_millis": 956650696,
          "total_auto_throttle_in_bytes": 83886080
        },
        "refresh": {
          "total": 196291,
          "total_time_in_millis": 85708949,
          "listeners": 0
        },
        "flush": {
          "total": 5761,
          "periodic": 5745,
          "total_time_in_millis": 5158163
        },
        "warmer": {
          "current": 0,
          "total": 190415,
          "total_time_in_millis": 9617
        },
        "query_cache": {
          "memory_size_in_bytes": 386553627,
          "total_count": 278690,
          "hit_count": 222355,
          "miss_count": 56335,
          "cache_size": 1028,
          "cache_count": 1028,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 721,
          "memory_in_bytes": 2655355555,
          "terms_memory_in_bytes": 2142820473,
          "stored_fields_memory_in_bytes": 459180312,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 53120814,
          "doc_values_memory_in_bytes": 233956,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542758403366,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 7086248,
          "size_in_bytes": 9042811953,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 880,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 2396729464,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 1156970597395
        },
        "indexing": {
          "index_total": 2396729464,
          "index_time_in_millis": 470876005,
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
          "query_total": 72063,
          "query_time_in_millis": 6961193,
          "query_current": 0,
          "fetch_total": 2655,
          "fetch_time_in_millis": 1773,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 46461,
          "total_time_in_millis": 1239514679,
          "total_docs": 7391380284,
          "total_size_in_bytes": 4267605661181,
          "total_stopped_time_in_millis": 16562,
          "total_throttled_time_in_millis": 956650696,
          "total_auto_throttle_in_bytes": 83886080
        },
        "refresh": {
          "total": 196291,
          "total_time_in_millis": 85708949,
          "listeners": 0
        },
        "flush": {
          "total": 5761,
          "periodic": 5745,
          "total_time_in_millis": 5158163
        },
        "warmer": {
          "current": 0,
          "total": 190415,
          "total_time_in_millis": 9617
        },
        "query_cache": {
          "memory_size_in_bytes": 386553627,
          "total_count": 278690,
          "hit_count": 222355,
          "miss_count": 56335,
          "cache_size": 1028,
          "cache_count": 1028,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 721,
          "memory_in_bytes": 2655355555,
          "terms_memory_in_bytes": 2142820473,
          "stored_fields_memory_in_bytes": 459180312,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 53120814,
          "doc_values_memory_in_bytes": 233956,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542758403366,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 7086248,
          "size_in_bytes": 9042811953,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 880,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 149800223,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72221131433
            },
            "indexing": {
              "index_total": 149800223,
              "index_time_in_millis": 29174945,
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
              "query_total": 4489,
              "query_time_in_millis": 385877,
              "query_current": 0,
              "fetch_total": 412,
              "fetch_time_in_millis": 393,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3118,
              "total_time_in_millis": 77892433,
              "total_docs": 475916485,
              "total_size_in_bytes": 274374598613,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 59901851,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12510,
              "total_time_in_millis": 4949620,
              "listeners": 0
            },
            "flush": {
              "total": 360,
              "periodic": 359,
              "total_time_in_millis": 306189
            },
            "warmer": {
              "current": 0,
              "total": 12147,
              "total_time_in_millis": 564
            },
            "query_cache": {
              "memory_size_in_bytes": 27000049,
              "total_count": 14756,
              "hit_count": 12254,
              "miss_count": 2502,
              "cache_size": 56,
              "cache_count": 56,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 50,
              "memory_in_bytes": 163618526,
              "terms_memory_in_bytes": 131372300,
              "stored_fields_memory_in_bytes": 28910320,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3320514,
              "doc_values_memory_in_bytes": 15392,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 434347,
              "size_in_bytes": 554183292,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22854225
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO813Q==",
              "generation": 363,
              "user_data": {
                "local_checkpoint": "149800222",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "Kzm0vS1sSG2WgXf5sX3Uog",
                "history_uuid": "vy5UlqdHS3i2-V41CAgb0w",
                "sync_id": "TQiQB9HDQ62xMX6RLAH88Q",
                "translog_generation": "2856",
                "max_seq_no": "149800222"
              },
              "num_docs": 149800223
            },
            "seq_no": {
              "max_seq_no": 149800222,
              "local_checkpoint": 149800222,
              "global_checkpoint": 149800222
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "1": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 149798060,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72231520638
            },
            "indexing": {
              "index_total": 149798060,
              "index_time_in_millis": 29637729,
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
              "query_total": 4509,
              "query_time_in_millis": 425823,
              "query_current": 0,
              "fetch_total": 6,
              "fetch_time_in_millis": 93,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3051,
              "total_time_in_millis": 77027310,
              "total_docs": 469719056,
              "total_size_in_bytes": 271185331551,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 59316247,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12201,
              "total_time_in_millis": 5338774,
              "listeners": 0
            },
            "flush": {
              "total": 360,
              "periodic": 359,
              "total_time_in_millis": 329437
            },
            "warmer": {
              "current": 0,
              "total": 11833,
              "total_time_in_millis": 540
            },
            "query_cache": {
              "memory_size_in_bytes": 24104551,
              "total_count": 19531,
              "hit_count": 15592,
              "miss_count": 3939,
              "cache_size": 72,
              "cache_count": 72,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 37,
              "memory_in_bytes": 161842778,
              "terms_memory_in_bytes": 129662022,
              "stored_fields_memory_in_bytes": 28847096,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3320064,
              "doc_values_memory_in_bytes": 13596,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 442294,
              "size_in_bytes": 564536713,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22857356
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB7Aow==",
              "generation": 364,
              "user_data": {
                "local_checkpoint": "149798059",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "uO5HXOAtQfGh1OXLt7R0kQ",
                "history_uuid": "auz9gy6NQ02BU4bJ96uvUg",
                "sync_id": "KSSrs-eiSMqFoFH9SUPr8g",
                "translog_generation": "2858",
                "max_seq_no": "149798059"
              },
              "num_docs": 149798060
            },
            "seq_no": {
              "max_seq_no": 149798059,
              "local_checkpoint": 149798059,
              "global_checkpoint": 149798059
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "2": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 149789357,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72477559929
            },
            "indexing": {
              "index_total": 149789357,
              "index_time_in_millis": 29991475,
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
              "query_total": 4509,
              "query_time_in_millis": 472404,
              "query_current": 0,
              "fetch_total": 3,
              "fetch_time_in_millis": 163,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3050,
              "total_time_in_millis": 78516121,
              "total_docs": 465270540,
              "total_size_in_bytes": 268820242883,
              "total_stopped_time_in_millis": 5786,
              "total_throttled_time_in_millis": 60505544,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12108,
              "total_time_in_millis": 5481546,
              "listeners": 0
            },
            "flush": {
              "total": 361,
              "periodic": 360,
              "total_time_in_millis": 348451
            },
            "warmer": {
              "current": 0,
              "total": 11743,
              "total_time_in_millis": 593
            },
            "query_cache": {
              "memory_size_in_bytes": 27629823,
              "total_count": 21489,
              "hit_count": 17509,
              "miss_count": 3980,
              "cache_size": 80,
              "cache_count": 80,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 44,
              "memory_in_bytes": 168758495,
              "terms_memory_in_bytes": 136596297,
              "stored_fields_memory_in_bytes": 28826256,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3320662,
              "doc_values_memory_in_bytes": 15280,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 468696,
              "size_in_bytes": 598055483,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22869463
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAY9g==",
              "generation": 364,
              "user_data": {
                "local_checkpoint": "149789356",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "pQqzxpEjSDWNHM8R_eKiHg",
                "history_uuid": "fi8tFA1ESNOwBQyS2X8aNQ",
                "sync_id": "ymIhins-Tsiw1D-IFg715Q",
                "translog_generation": "2863",
                "max_seq_no": "149789356"
              },
              "num_docs": 149789357
            },
            "seq_no": {
              "max_seq_no": 149789356,
              "local_checkpoint": 149789356,
              "global_checkpoint": 149789356
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "3": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 149815888,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72326077327
            },
            "indexing": {
              "index_total": 149815888,
              "index_time_in_millis": 30850201,
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
              "query_total": 4509,
              "query_time_in_millis": 519274,
              "query_current": 0,
              "fetch_total": 6,
              "fetch_time_in_millis": 61,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 3139,
              "total_time_in_millis": 77798649,
              "total_docs": 471160533,
              "total_size_in_bytes": 272189421087,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 59102548,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12364,
              "total_time_in_millis": 5121385,
              "listeners": 0
            },
            "flush": {
              "total": 362,
              "periodic": 361,
              "total_time_in_millis": 305938
            },
            "warmer": {
              "current": 0,
              "total": 11991,
              "total_time_in_millis": 738
            },
            "query_cache": {
              "memory_size_in_bytes": 29139179,
              "total_count": 16855,
              "hit_count": 12999,
              "miss_count": 3856,
              "cache_size": 60,
              "cache_count": 60,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 41,
              "memory_in_bytes": 164627830,
              "terms_memory_in_bytes": 132398422,
              "stored_fields_memory_in_bytes": 28888768,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3323396,
              "doc_values_memory_in_bytes": 17244,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403366,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 454295,
              "size_in_bytes": 579790823,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22862484
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGZuKg==",
              "generation": 366,
              "user_data": {
                "local_checkpoint": "149815887",
                "max_unsafe_auto_id_timestamp": "1542758403366",
                "translog_uuid": "Q3PeYoICTTyTkynL6x26tg",
                "history_uuid": "YEgZFJKDRE6ow6Z92Wvkag",
                "sync_id": "c7hx_ovRTd-8HYk1rMKvZQ",
                "translog_generation": "2865",
                "max_seq_no": "149815887"
              },
              "num_docs": 149815888
            },
            "seq_no": {
              "max_seq_no": 149815887,
              "local_checkpoint": 149815887,
              "global_checkpoint": 149815887
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "4": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 149795494,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72370895169
            },
            "indexing": {
              "index_total": 149795494,
              "index_time_in_millis": 29169785,
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
              "query_total": 4489,
              "query_time_in_millis": 370977,
              "query_current": 0,
              "fetch_total": 2,
              "fetch_time_in_millis": 99,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2913,
              "total_time_in_millis": 76378582,
              "total_docs": 462500980,
              "total_size_in_bytes": 267178604037,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 58986238,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12444,
              "total_time_in_millis": 5108467,
              "listeners": 0
            },
            "flush": {
              "total": 359,
              "periodic": 358,
              "total_time_in_millis": 303578
            },
            "warmer": {
              "current": 0,
              "total": 12080,
              "total_time_in_millis": 607
            },
            "query_cache": {
              "memory_size_in_bytes": 21461673,
              "total_count": 15559,
              "hit_count": 13115,
              "miss_count": 2444,
              "cache_size": 60,
              "cache_count": 60,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 44,
              "memory_in_bytes": 165574617,
              "terms_memory_in_bytes": 133423076,
              "stored_fields_memory_in_bytes": 28812256,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3321525,
              "doc_values_memory_in_bytes": 17760,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 447714,
              "size_in_bytes": 571282334,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22858883
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO86mg==",
              "generation": 363,
              "user_data": {
                "local_checkpoint": "149795493",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "SeuOK83CSgK5eUo_mM_oqQ",
                "history_uuid": "A7T-EE66R6mmhAzOtAGEYw",
                "sync_id": "VVosRLURTMmUgd7YC9u4nA",
                "translog_generation": "2857",
                "max_seq_no": "149795493"
              },
              "num_docs": 149795494
            },
            "seq_no": {
              "max_seq_no": 149795493,
              "local_checkpoint": 149795493,
              "global_checkpoint": 149795493
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "5": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 149786590,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72352717210
            },
            "indexing": {
              "index_total": 149786590,
              "index_time_in_millis": 29861504,
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
              "query_total": 4509,
              "query_time_in_millis": 427787,
              "query_current": 0,
              "fetch_total": 2,
              "fetch_time_in_millis": 163,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2853,
              "total_time_in_millis": 76862888,
              "total_docs": 464203598,
              "total_size_in_bytes": 267635476790,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 59666866,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12141,
              "total_time_in_millis": 5464752,
              "listeners": 0
            },
            "flush": {
              "total": 360,
              "periodic": 359,
              "total_time_in_millis": 337707
            },
            "warmer": {
              "current": 0,
              "total": 11777,
              "total_time_in_millis": 613
            },
            "query_cache": {
              "memory_size_in_bytes": 27594302,
              "total_count": 18252,
              "hit_count": 14531,
              "miss_count": 3721,
              "cache_size": 68,
              "cache_count": 68,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 49,
              "memory_in_bytes": 168807673,
              "terms_memory_in_bytes": 136722173,
              "stored_fields_memory_in_bytes": 28743984,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3323976,
              "doc_values_memory_in_bytes": 17540,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 430034,
              "size_in_bytes": 548648663,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22851307
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB62/Q==",
              "generation": 363,
              "user_data": {
                "local_checkpoint": "149786589",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "HR_C1JAPQjydruQZ29fvKQ",
                "history_uuid": "vd3xlV6QQtiKjzwCPRExGg",
                "sync_id": "3xjF1sfmQzmZflHzRFZsIw",
                "translog_generation": "2857",
                "max_seq_no": "149786589"
              },
              "num_docs": 149786590
            },
            "seq_no": {
              "max_seq_no": 149786589,
              "local_checkpoint": 149786589,
              "global_checkpoint": 149786589
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "6": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 149794328,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72150443837
            },
            "indexing": {
              "index_total": 149794328,
              "index_time_in_millis": 29848463,
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
              "query_total": 4509,
              "query_time_in_millis": 452447,
              "query_current": 0,
              "fetch_total": 904,
              "fetch_time_in_millis": 521,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2852,
              "total_time_in_millis": 76903001,
              "total_docs": 462041753,
              "total_size_in_bytes": 266698978402,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 59274212,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12050,
              "total_time_in_millis": 5656388,
              "listeners": 0
            },
            "flush": {
              "total": 359,
              "periodic": 358,
              "total_time_in_millis": 342059
            },
            "warmer": {
              "current": 0,
              "total": 11683,
              "total_time_in_millis": 627
            },
            "query_cache": {
              "memory_size_in_bytes": 22955570,
              "total_count": 17537,
              "hit_count": 13931,
              "miss_count": 3606,
              "cache_size": 64,
              "cache_count": 64,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 44,
              "memory_in_bytes": 161131526,
              "terms_memory_in_bytes": 129068718,
              "stored_fields_memory_in_bytes": 28728520,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3321984,
              "doc_values_memory_in_bytes": 12304,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 443013,
              "size_in_bytes": 565403201,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22857771
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAY+Q==",
              "generation": 362,
              "user_data": {
                "local_checkpoint": "149794327",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "SkHlP4F0RfyldHhQuGag6Q",
                "history_uuid": "Y8QBrQ5GTLKCGOhPNUETuA",
                "sync_id": "Ljv4sc-QTW6Fg6AX5EPnJA",
                "translog_generation": "2853",
                "max_seq_no": "149794327"
              },
              "num_docs": 149794328
            },
            "seq_no": {
              "max_seq_no": 149794327,
              "local_checkpoint": 149794327,
              "global_checkpoint": 149794327
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "7": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 149801708,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72618791956
            },
            "indexing": {
              "index_total": 149801708,
              "index_time_in_millis": 30898030,
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
              "query_total": 4509,
              "query_time_in_millis": 494235,
              "query_current": 0,
              "fetch_total": 407,
              "fetch_time_in_millis": 62,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2918,
              "total_time_in_millis": 76954351,
              "total_docs": 451740829,
              "total_size_in_bytes": 261863643633,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 59303060,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12290,
              "total_time_in_millis": 5296774,
              "listeners": 0
            },
            "flush": {
              "total": 359,
              "periodic": 358,
              "total_time_in_millis": 307044
            },
            "warmer": {
              "current": 0,
              "total": 11926,
              "total_time_in_millis": 613
            },
            "query_cache": {
              "memory_size_in_bytes": 23379963,
              "total_count": 17851,
              "hit_count": 13865,
              "miss_count": 3986,
              "cache_size": 64,
              "cache_count": 64,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 44,
              "memory_in_bytes": 170972981,
              "terms_memory_in_bytes": 138855996,
              "stored_fields_memory_in_bytes": 28783928,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3319393,
              "doc_values_memory_in_bytes": 13664,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403366,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 447521,
              "size_in_bytes": 571072261,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22860010
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGZogA==",
              "generation": 363,
              "user_data": {
                "local_checkpoint": "149801707",
                "max_unsafe_auto_id_timestamp": "1542758403366",
                "translog_uuid": "lvNagn4AS9ecwWsLh8GeRQ",
                "history_uuid": "nyOyJnyVTviXwJDMGPhFnQ",
                "sync_id": "Upzj8gHPSJuIcYbtitEFog",
                "translog_generation": "2859",
                "max_seq_no": "149801707"
              },
              "num_docs": 149801708
            },
            "seq_no": {
              "max_seq_no": 149801707,
              "local_checkpoint": 149801707,
              "global_checkpoint": 149801707
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "8": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 149786359,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72663263291
            },
            "indexing": {
              "index_total": 149786359,
              "index_time_in_millis": 28724162,
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
              "query_total": 4489,
              "query_time_in_millis": 358453,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2836,
              "total_time_in_millis": 76224710,
              "total_docs": 456546800,
              "total_size_in_bytes": 263853995511,
              "total_stopped_time_in_millis": 4065,
              "total_throttled_time_in_millis": 58820414,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12510,
              "total_time_in_millis": 5012606,
              "listeners": 0
            },
            "flush": {
              "total": 359,
              "periodic": 358,
              "total_time_in_millis": 293561
            },
            "warmer": {
              "current": 0,
              "total": 12144,
              "total_time_in_millis": 634
            },
            "query_cache": {
              "memory_size_in_bytes": 17302681,
              "total_count": 13805,
              "hit_count": 11292,
              "miss_count": 2513,
              "cache_size": 52,
              "cache_count": 52,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 49,
              "memory_in_bytes": 177587446,
              "terms_memory_in_bytes": 145481693,
              "stored_fields_memory_in_bytes": 28762568,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3323621,
              "doc_values_memory_in_bytes": 19564,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 433761,
              "size_in_bytes": 553547419,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22854079
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO813g==",
              "generation": 362,
              "user_data": {
                "local_checkpoint": "149786358",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "zJFzQl4ET-CrtHgiWdctdA",
                "history_uuid": "YqepgISNT6-Rc9Q5TlWgsQ",
                "sync_id": "vkzLCTzOQtKMWYYeHqZk9w",
                "translog_generation": "2860",
                "max_seq_no": "149786358"
              },
              "num_docs": 149786359
            },
            "seq_no": {
              "max_seq_no": 149786358,
              "local_checkpoint": 149786358,
              "global_checkpoint": 149786358
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "9": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 149797591,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72035950034
            },
            "indexing": {
              "index_total": 149797591,
              "index_time_in_millis": 29338845,
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
              "query_total": 4509,
              "query_time_in_millis": 417497,
              "query_current": 0,
              "fetch_total": 16,
              "fetch_time_in_millis": 8,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2801,
              "total_time_in_millis": 77373571,
              "total_docs": 467420542,
              "total_size_in_bytes": 269253878148,
              "total_stopped_time_in_millis": 4941,
              "total_throttled_time_in_millis": 59832904,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12205,
              "total_time_in_millis": 5416307,
              "listeners": 0
            },
            "flush": {
              "total": 360,
              "periodic": 359,
              "total_time_in_millis": 327903
            },
            "warmer": {
              "current": 0,
              "total": 11835,
              "total_time_in_millis": 555
            },
            "query_cache": {
              "memory_size_in_bytes": 26772894,
              "total_count": 18313,
              "hit_count": 14484,
              "miss_count": 3829,
              "cache_size": 68,
              "cache_count": 68,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 42,
              "memory_in_bytes": 158060789,
              "terms_memory_in_bytes": 126014912,
              "stored_fields_memory_in_bytes": 28717656,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3318965,
              "doc_values_memory_in_bytes": 9256,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 449815,
              "size_in_bytes": 574045519,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22860368
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB63Tg==",
              "generation": 364,
              "user_data": {
                "local_checkpoint": "149797590",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "Azwd624CTbOvcfUgK1iojQ",
                "history_uuid": "otm2pReOT9-dAHAj9686dQ",
                "sync_id": "H4m68AnKQNGRTeyG5Tr4qw",
                "translog_generation": "2859",
                "max_seq_no": "149797590"
              },
              "num_docs": 149797591
            },
            "seq_no": {
              "max_seq_no": 149797590,
              "local_checkpoint": 149797590,
              "global_checkpoint": 149797590
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "10": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 149800164,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72291544509
            },
            "indexing": {
              "index_total": 149800164,
              "index_time_in_millis": 29221350,
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
              "query_total": 4509,
              "query_time_in_millis": 470781,
              "query_current": 0,
              "fetch_total": 5,
              "fetch_time_in_millis": 147,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2750,
              "total_time_in_millis": 78258543,
              "total_docs": 456100657,
              "total_size_in_bytes": 263438567901,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 60730108,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12103,
              "total_time_in_millis": 5576187,
              "listeners": 0
            },
            "flush": {
              "total": 360,
              "periodic": 359,
              "total_time_in_millis": 339250
            },
            "warmer": {
              "current": 0,
              "total": 11735,
              "total_time_in_millis": 608
            },
            "query_cache": {
              "memory_size_in_bytes": 21773692,
              "total_count": 15905,
              "hit_count": 12035,
              "miss_count": 3870,
              "cache_size": 56,
              "cache_count": 56,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 47,
              "memory_in_bytes": 163952441,
              "terms_memory_in_bytes": 131936864,
              "stored_fields_memory_in_bytes": 28682880,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3317901,
              "doc_values_memory_in_bytes": 14796,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 449767,
              "size_in_bytes": 573974972,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22860726
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAaMQ==",
              "generation": 364,
              "user_data": {
                "local_checkpoint": "149800163",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "rfkzrt66QeSI3tWLod6Xdg",
                "history_uuid": "4nXLwiGvSruEbe42n7XOZA",
                "sync_id": "NYa-FI24TQejzPHkIzjn6Q",
                "translog_generation": "2853",
                "max_seq_no": "149800163"
              },
              "num_docs": 149800164
            },
            "seq_no": {
              "max_seq_no": 149800163,
              "local_checkpoint": 149800163,
              "global_checkpoint": 149800163
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "11": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 149787225,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72672004976
            },
            "indexing": {
              "index_total": 149787225,
              "index_time_in_millis": 30217426,
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
              "query_total": 4509,
              "query_time_in_millis": 515288,
              "query_current": 0,
              "fetch_total": 3,
              "fetch_time_in_millis": 5,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2824,
              "total_time_in_millis": 76638369,
              "total_docs": 449756388,
              "total_size_in_bytes": 260631098966,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 58726603,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12360,
              "total_time_in_millis": 5178424,
              "listeners": 0
            },
            "flush": {
              "total": 361,
              "periodic": 360,
              "total_time_in_millis": 313240
            },
            "warmer": {
              "current": 0,
              "total": 11989,
              "total_time_in_millis": 614
            },
            "query_cache": {
              "memory_size_in_bytes": 23115787,
              "total_count": 17102,
              "hit_count": 13013,
              "miss_count": 4089,
              "cache_size": 60,
              "cache_count": 60,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 51,
              "memory_in_bytes": 174247563,
              "terms_memory_in_bytes": 142171155,
              "stored_fields_memory_in_bytes": 28744064,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3320036,
              "doc_values_memory_in_bytes": 12308,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403366,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 427523,
              "size_in_bytes": 545588230,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22849610
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGZleA==",
              "generation": 364,
              "user_data": {
                "local_checkpoint": "149787224",
                "max_unsafe_auto_id_timestamp": "1542758403366",
                "translog_uuid": "aa9Z5V8BRl-FM-nLt9Hc0g",
                "history_uuid": "a9esyyuXSXS_x-vaujsVcw",
                "sync_id": "r88jKozAQTmuLl78f3BnXg",
                "translog_generation": "2854",
                "max_seq_no": "149787224"
              },
              "num_docs": 149787225
            },
            "seq_no": {
              "max_seq_no": 149787224,
              "local_checkpoint": 149787224,
              "global_checkpoint": 149787224
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "12": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 149784141,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72088357153
            },
            "indexing": {
              "index_total": 149784141,
              "index_time_in_millis": 27818040,
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
              "query_total": 4488,
              "query_time_in_millis": 326330,
              "query_current": 0,
              "fetch_total": 1,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2868,
              "total_time_in_millis": 77881032,
              "total_docs": 463101272,
              "total_size_in_bytes": 267023372374,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 60376576,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12463,
              "total_time_in_millis": 5222590,
              "listeners": 0
            },
            "flush": {
              "total": 360,
              "periodic": 359,
              "total_time_in_millis": 297656
            },
            "warmer": {
              "current": 0,
              "total": 12096,
              "total_time_in_millis": 566
            },
            "query_cache": {
              "memory_size_in_bytes": 25669217,
              "total_count": 16335,
              "hit_count": 13879,
              "miss_count": 2456,
              "cache_size": 64,
              "cache_count": 64,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 44,
              "memory_in_bytes": 161099896,
              "terms_memory_in_bytes": 129309682,
              "stored_fields_memory_in_bytes": 28455656,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3316134,
              "doc_values_memory_in_bytes": 18424,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 428477,
              "size_in_bytes": 546773372,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22850919
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO8/LQ==",
              "generation": 364,
              "user_data": {
                "local_checkpoint": "149784140",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "PdoUbkZCTDiyKjH3y-J6LA",
                "history_uuid": "CJBTrK2GTTqKLi6aOSom_g",
                "sync_id": "gbZN2MZKTeKJYIhILzsjzA",
                "translog_generation": "2862",
                "max_seq_no": "149784140"
              },
              "num_docs": 149784141
            },
            "seq_no": {
              "max_seq_no": 149784140,
              "local_checkpoint": 149784140,
              "global_checkpoint": 149784140
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "13": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 149792924,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72049990396
            },
            "indexing": {
              "index_total": 149792924,
              "index_time_in_millis": 28251736,
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
              "query_total": 4509,
              "query_time_in_millis": 413181,
              "query_current": 0,
              "fetch_total": 885,
              "fetch_time_in_millis": 55,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2834,
              "total_time_in_millis": 77698478,
              "total_docs": 461662441,
              "total_size_in_bytes": 265989538156,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 60303382,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12179,
              "total_time_in_millis": 5594080,
              "listeners": 0
            },
            "flush": {
              "total": 360,
              "periodic": 359,
              "total_time_in_millis": 344524
            },
            "warmer": {
              "current": 0,
              "total": 11812,
              "total_time_in_millis": 563
            },
            "query_cache": {
              "memory_size_in_bytes": 21035806,
              "total_count": 18316,
              "hit_count": 14571,
              "miss_count": 3745,
              "cache_size": 68,
              "cache_count": 68,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 48,
              "memory_in_bytes": 161668463,
              "terms_memory_in_bytes": 129894340,
              "stored_fields_memory_in_bytes": 28445792,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3314547,
              "doc_values_memory_in_bytes": 13784,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 438177,
              "size_in_bytes": 559149750,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22855609
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB63AA==",
              "generation": 363,
              "user_data": {
                "local_checkpoint": "149792923",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "UutTgnTHQWyLH-4TtPaqTA",
                "history_uuid": "hHqNOgx6Rdie10IhgUzGFA",
                "sync_id": "S6JcoCB8R22sOJtk-D1Qag",
                "translog_generation": "2865",
                "max_seq_no": "149792923"
              },
              "num_docs": 149792924
            },
            "seq_no": {
              "max_seq_no": 149792923,
              "local_checkpoint": 149792923,
              "global_checkpoint": 149792923
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "14": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 149802800,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72121076445
            },
            "indexing": {
              "index_total": 149802800,
              "index_time_in_millis": 28538447,
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
              "query_total": 4509,
              "query_time_in_millis": 436646,
              "query_current": 0,
              "fetch_total": 3,
              "fetch_time_in_millis": 3,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2788,
              "total_time_in_millis": 78913488,
              "total_docs": 454036051,
              "total_size_in_bytes": 262162460246,
              "total_stopped_time_in_millis": 1770,
              "total_throttled_time_in_millis": 61665608,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12057,
              "total_time_in_millis": 5833147,
              "listeners": 0
            },
            "flush": {
              "total": 361,
              "periodic": 360,
              "total_time_in_millis": 352636
            },
            "warmer": {
              "current": 0,
              "total": 11689,
              "total_time_in_millis": 575
            },
            "query_cache": {
              "memory_size_in_bytes": 25543165,
              "total_count": 18465,
              "hit_count": 14540,
              "miss_count": 3925,
              "cache_size": 68,
              "cache_count": 68,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 39,
              "memory_in_bytes": 162981973,
              "terms_memory_in_bytes": 131253111,
              "stored_fields_memory_in_bytes": 28402328,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3317218,
              "doc_values_memory_in_bytes": 9316,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403072,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 450747,
              "size_in_bytes": 575143212,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22860794
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAiOA==",
              "generation": 365,
              "user_data": {
                "local_checkpoint": "149802799",
                "max_unsafe_auto_id_timestamp": "1542758403072",
                "translog_uuid": "rWIdCzeTQzCujFAMFoeWsw",
                "history_uuid": "OQUesvs3QEa_KvvsS-isFw",
                "sync_id": "qburyl8LRAqvUbgNoGQf-A",
                "translog_generation": "2858",
                "max_seq_no": "149802799"
              },
              "num_docs": 149802800
            },
            "seq_no": {
              "max_seq_no": 149802799,
              "local_checkpoint": 149802799,
              "global_checkpoint": 149802799
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "15": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 149796612,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 72299273092
            },
            "indexing": {
              "index_total": 149796612,
              "index_time_in_millis": 29333867,
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
              "query_total": 4509,
              "query_time_in_millis": 474193,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2866,
              "total_time_in_millis": 78193153,
              "total_docs": 460202359,
              "total_size_in_bytes": 265306452883,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 60138535,
              "total_auto_throttle_in_bytes": 5242880
            },
            "refresh": {
              "total": 12306,
              "total_time_in_millis": 5457902,
              "listeners": 0
            },
            "flush": {
              "total": 360,
              "periodic": 359,
              "total_time_in_millis": 308990
            },
            "warmer": {
              "current": 0,
              "total": 11935,
              "total_time_in_millis": 607
            },
            "query_cache": {
              "memory_size_in_bytes": 22075275,
              "total_count": 18619,
              "hit_count": 14745,
              "miss_count": 3874,
              "cache_size": 68,
              "cache_count": 68,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 48,
              "memory_in_bytes": 170422558,
              "terms_memory_in_bytes": 138659712,
              "stored_fields_memory_in_bytes": 28428240,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3320878,
              "doc_values_memory_in_bytes": 13728,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403366,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 440067,
              "size_in_bytes": 561616709,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22856237
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGZlfA==",
              "generation": 363,
              "user_data": {
                "local_checkpoint": "149796611",
                "max_unsafe_auto_id_timestamp": "1542758403366",
                "translog_uuid": "TM_L6ssMQuuXAb8GUxD69w",
                "history_uuid": "rxTXUy6HRzajBLjifOsimw",
                "sync_id": "bZJ6y7X5RPGmBqpEYXKl0Q",
                "translog_generation": "2859",
                "max_seq_no": "149796611"
              },
              "num_docs": 149796612
            },
            "seq_no": {
              "max_seq_no": 149796611,
              "local_checkpoint": 149796611,
              "global_checkpoint": 149796611
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".kibana_1": {
      "uuid": "hQvndrMFSHuQtrV9_47r-Q",
      "primaries": {
        "docs": {
          "count": 2,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 18361
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 25,
          "query_time_in_millis": 1,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 3,
          "total_time_in_millis": 0,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 1,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 1,
          "memory_in_bytes": 2743,
          "terms_memory_in_bytes": 2169,
          "stored_fields_memory_in_bytes": 312,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 192,
          "points_memory_in_bytes": 2,
          "doc_values_memory_in_bytes": 68,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 275,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 275,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 4,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 36722
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 45,
          "query_time_in_millis": 1,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 6,
          "total_time_in_millis": 1,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 2,
          "total_time_in_millis": 0
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 2,
          "memory_in_bytes": 5486,
          "terms_memory_in_bytes": 4338,
          "stored_fields_memory_in_bytes": 624,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 384,
          "points_memory_in_bytes": 4,
          "doc_values_memory_in_bytes": 136,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 385,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 385,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 2,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 18361
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 20,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 1,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 1,
              "memory_in_bytes": 2743,
              "terms_memory_in_bytes": 2169,
              "stored_fields_memory_in_bytes": 312,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 192,
              "points_memory_in_bytes": 2,
              "doc_values_memory_in_bytes": 68,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 110,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 110,
              "earliest_last_modified_age": 234486942
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbObgiw==",
              "generation": 8,
              "user_data": {
                "local_checkpoint": "1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "hTKNswdFSnm8mTnZvUIwbw",
                "history_uuid": "YZHkrF60Q0OMnqn_KKKpbg",
                "sync_id": "BEVzqxhsSKS20DW-Fpr0_w",
                "translog_generation": "1",
                "max_seq_no": "1"
              },
              "num_docs": 2
            },
            "seq_no": {
              "max_seq_no": 1,
              "local_checkpoint": 1,
              "global_checkpoint": 1
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 2,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 18361
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 25,
              "query_time_in_millis": 1,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 0,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 1,
              "memory_in_bytes": 2743,
              "terms_memory_in_bytes": 2169,
              "stored_fields_memory_in_bytes": 312,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 192,
              "points_memory_in_bytes": 2,
              "doc_values_memory_in_bytes": 68,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 275,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 275,
              "earliest_last_modified_age": 236342341
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "CZlg6aXrV4r1ozllcWfP2A==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "zHkw7zXgSPikZ-KtzybPug",
                "history_uuid": "YZHkrF60Q0OMnqn_KKKpbg",
                "sync_id": "BEVzqxhsSKS20DW-Fpr0_w",
                "translog_generation": "1",
                "max_seq_no": "1"
              },
              "num_docs": 2
            },
            "seq_no": {
              "max_seq_no": 1,
              "local_checkpoint": 1,
              "global_checkpoint": 1
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".tasks": {
      "uuid": "OZFcFrH_TymIlCb3ZnM_Pw",
      "primaries": {
        "docs": {
          "count": 1,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 6362
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 24,
          "query_time_in_millis": 0,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 3,
          "total_time_in_millis": 0,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 1,
          "total_time_in_millis": 1
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 1,
          "memory_in_bytes": 2089,
          "terms_memory_in_bytes": 1639,
          "stored_fields_memory_in_bytes": 312,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 64,
          "points_memory_in_bytes": 6,
          "doc_values_memory_in_bytes": 68,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 275,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 275,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 2,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 12724
        },
        "indexing": {
          "index_total": 0,
          "index_time_in_millis": 0,
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
          "query_total": 45,
          "query_time_in_millis": 0,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 0,
          "total_time_in_millis": 0,
          "total_docs": 0,
          "total_size_in_bytes": 0,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 6,
          "total_time_in_millis": 3,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 2,
          "total_time_in_millis": 1
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 2,
          "memory_in_bytes": 4178,
          "terms_memory_in_bytes": 3278,
          "stored_fields_memory_in_bytes": 624,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 128,
          "points_memory_in_bytes": 12,
          "doc_values_memory_in_bytes": 136,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 385,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 385,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 1,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 6362
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 24,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 0,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 1
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 1,
              "memory_in_bytes": 2089,
              "terms_memory_in_bytes": 1639,
              "stored_fields_memory_in_bytes": 312,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 64,
              "points_memory_in_bytes": 6,
              "doc_values_memory_in_bytes": 68,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 275,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 275,
              "earliest_last_modified_age": 509190385
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "e/41VvJpR+9whsmTEF1TcQ==",
              "generation": 4,
              "user_data": {
                "local_checkpoint": "0",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "XR1xzVCnTuugDvsxTizmKg",
                "history_uuid": "bN27-WvvRnCE_KqFro-Qgg",
                "sync_id": "OXlkugOPQT-DR8DIvRhjWg",
                "translog_generation": "3",
                "max_seq_no": "0"
              },
              "num_docs": 1
            },
            "seq_no": {
              "max_seq_no": 0,
              "local_checkpoint": 0,
              "global_checkpoint": 0
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 1,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 6362
            },
            "indexing": {
              "index_total": 0,
              "index_time_in_millis": 0,
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
              "query_total": 21,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 0,
              "total_time_in_millis": 0,
              "total_docs": 0,
              "total_size_in_bytes": 0,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 3,
              "total_time_in_millis": 3,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1,
              "total_time_in_millis": 0
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 1,
              "memory_in_bytes": 2089,
              "terms_memory_in_bytes": 1639,
              "stored_fields_memory_in_bytes": 312,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 64,
              "points_memory_in_bytes": 6,
              "doc_values_memory_in_bytes": 68,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 110,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 110,
              "earliest_last_modified_age": 234566923
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWF0kgA==",
              "generation": 5,
              "user_data": {
                "local_checkpoint": "0",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "AitxOuj-QTqbq7UDnAPy8w",
                "history_uuid": "bN27-WvvRnCE_KqFro-Qgg",
                "sync_id": "OXlkugOPQT-DR8DIvRhjWg",
                "translog_generation": "1",
                "max_seq_no": "0"
              },
              "num_docs": 1
            },
            "seq_no": {
              "max_seq_no": 0,
              "local_checkpoint": 0,
              "global_checkpoint": 0
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    "metricbeat-6.5.0-2018.11.20": {
      "uuid": "d6tCJ7QJSB-1IO6fDGW1Yw",
      "primaries": {
        "docs": {
          "count": 3399066,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2433154489
        },
        "indexing": {
          "index_total": 3399066,
          "index_time_in_millis": 1515320,
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
          "query_total": 315,
          "query_time_in_millis": 1791,
          "query_current": 0,
          "fetch_total": 1,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 11204,
          "total_time_in_millis": 1984712,
          "total_docs": 26515259,
          "total_size_in_bytes": 29492769184,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 84626,
          "total_auto_throttle_in_bytes": 75916299
        },
        "refresh": {
          "total": 70431,
          "total_time_in_millis": 3178987,
          "listeners": 0
        },
        "flush": {
          "total": 15,
          "periodic": 10,
          "total_time_in_millis": 2277
        },
        "warmer": {
          "current": 0,
          "total": 70406,
          "total_time_in_millis": 23442
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 1714,
          "hit_count": 0,
          "miss_count": 1714,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 86,
          "memory_in_bytes": 6405592,
          "terms_memory_in_bytes": 1703013,
          "stored_fields_memory_in_bytes": 1006968,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 465971,
          "doc_values_memory_in_bytes": 3229640,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 275,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 275,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 33,
          "miss_count": 172
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 6798132,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 4870666343
        },
        "indexing": {
          "index_total": 6798132,
          "index_time_in_millis": 2917919,
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
          "query_total": 635,
          "query_time_in_millis": 4593,
          "query_current": 0,
          "fetch_total": 3,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 21547,
          "total_time_in_millis": 3969071,
          "total_docs": 51466764,
          "total_size_in_bytes": 57378340731,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 168371,
          "total_auto_throttle_in_bytes": 144931115
        },
        "refresh": {
          "total": 140322,
          "total_time_in_millis": 6313914,
          "listeners": 0
        },
        "flush": {
          "total": 30,
          "periodic": 20,
          "total_time_in_millis": 4439
        },
        "warmer": {
          "current": 0,
          "total": 140274,
          "total_time_in_millis": 46305
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 3931,
          "hit_count": 0,
          "miss_count": 3931,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 183,
          "memory_in_bytes": 12615435,
          "terms_memory_in_bytes": 3531094,
          "stored_fields_memory_in_bytes": 2016480,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 943961,
          "doc_values_memory_in_bytes": 6123900,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542672001736,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 550,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 550,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 71,
          "miss_count": 339
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 679341,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 484073728
            },
            "indexing": {
              "index_total": 679341,
              "index_time_in_millis": 288520,
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
              "query_total": 59,
              "query_time_in_millis": 132,
              "query_current": 0,
              "fetch_total": 1,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2129,
              "total_time_in_millis": 425242,
              "total_docs": 5356906,
              "total_size_in_bytes": 5875527760,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 18313,
              "total_auto_throttle_in_bytes": 15756213
            },
            "refresh": {
              "total": 14045,
              "total_time_in_millis": 615954,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 449
            },
            "warmer": {
              "current": 0,
              "total": 14040,
              "total_time_in_millis": 4822
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 263,
              "hit_count": 0,
              "miss_count": 263,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 16,
              "memory_in_bytes": 1560621,
              "terms_memory_in_bytes": 324332,
              "stored_fields_memory_in_bytes": 200824,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 89737,
              "doc_values_memory_in_bytes": 945728,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688641
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5,
              "miss_count": 36
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOwp/A==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "679340",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "pne4r4AxTmu562iH1PQC3Q",
                "history_uuid": "mZblQrUwT3yQ4kSZn4XJlw",
                "sync_id": "pjDvqZWAQzS6o968YDiZaQ",
                "translog_generation": "19",
                "max_seq_no": "679340"
              },
              "num_docs": 679341
            },
            "seq_no": {
              "max_seq_no": 679340,
              "local_checkpoint": 679340,
              "global_checkpoint": 679340
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 679341,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 486715883
            },
            "indexing": {
              "index_total": 679341,
              "index_time_in_millis": 286846,
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
              "query_total": 68,
              "query_time_in_millis": 829,
              "query_current": 0,
              "fetch_total": 2,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2072,
              "total_time_in_millis": 435632,
              "total_docs": 4998085,
              "total_size_in_bytes": 5588444748,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 15803,
              "total_auto_throttle_in_bytes": 14323830
            },
            "refresh": {
              "total": 13917,
              "total_time_in_millis": 670118,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 502
            },
            "warmer": {
              "current": 0,
              "total": 13912,
              "total_time_in_millis": 4909
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 428,
              "hit_count": 0,
              "miss_count": 428,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 19,
              "memory_in_bytes": 1235644,
              "terms_memory_in_bytes": 360478,
              "stored_fields_memory_in_bytes": 200856,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 93554,
              "doc_values_memory_in_bytes": 580756,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688469
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 9,
              "miss_count": 32
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBur1Q==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "679340",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "6RMQ84qIR9ahXhvDcWe9Zw",
                "history_uuid": "mZblQrUwT3yQ4kSZn4XJlw",
                "sync_id": "pjDvqZWAQzS6o968YDiZaQ",
                "translog_generation": "19",
                "max_seq_no": "679340"
              },
              "num_docs": 679341
            },
            "seq_no": {
              "max_seq_no": 679340,
              "local_checkpoint": 679340,
              "global_checkpoint": 679340
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "1": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 681404,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 490140713
            },
            "indexing": {
              "index_total": 681404,
              "index_time_in_millis": 308350,
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
              "query_total": 63,
              "query_time_in_millis": 1088,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2308,
              "total_time_in_millis": 429504,
              "total_docs": 5203102,
              "total_size_in_bytes": 5877370273,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 15039,
              "total_auto_throttle_in_bytes": 14323830
            },
            "refresh": {
              "total": 14053,
              "total_time_in_millis": 692623,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 456
            },
            "warmer": {
              "current": 0,
              "total": 14048,
              "total_time_in_millis": 5221
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 455,
              "hit_count": 0,
              "miss_count": 455,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 18,
              "memory_in_bytes": 1174639,
              "terms_memory_in_bytes": 346274,
              "stored_fields_memory_in_bytes": 201400,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 96325,
              "doc_values_memory_in_bytes": 530640,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108687463
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 8,
              "miss_count": 33
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBur4A==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "681403",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "ceHvz2aaS9S6-ff1LdhfAg",
                "history_uuid": "YO0HbiSHTIW8YmVOxhUIlQ",
                "sync_id": "6ATdL8MHTjiJdlsuBUyE8A",
                "translog_generation": "19",
                "max_seq_no": "681403"
              },
              "num_docs": 681404
            },
            "seq_no": {
              "max_seq_no": 681403,
              "local_checkpoint": 681403,
              "global_checkpoint": 681403
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 681404,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 487914678
            },
            "indexing": {
              "index_total": 681404,
              "index_time_in_millis": 262441,
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
              "query_total": 64,
              "query_time_in_millis": 161,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2020,
              "total_time_in_millis": 386418,
              "total_docs": 4947090,
              "total_size_in_bytes": 5516598298,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 19382,
              "total_auto_throttle_in_bytes": 13021663
            },
            "refresh": {
              "total": 14039,
              "total_time_in_millis": 617331,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 518
            },
            "warmer": {
              "current": 0,
              "total": 14035,
              "total_time_in_millis": 4315
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 464,
              "hit_count": 0,
              "miss_count": 464,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 16,
              "memory_in_bytes": 1312981,
              "terms_memory_in_bytes": 327387,
              "stored_fields_memory_in_bytes": 201552,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 94378,
              "doc_values_memory_in_bytes": 689664,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672001736,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108687485
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5,
              "miss_count": 36
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AryL1g==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "681403",
                "max_unsafe_auto_id_timestamp": "1542672001736",
                "translog_uuid": "bA8OLrIYRfumjNVYKYEJFQ",
                "history_uuid": "YO0HbiSHTIW8YmVOxhUIlQ",
                "sync_id": "6ATdL8MHTjiJdlsuBUyE8A",
                "translog_generation": "19",
                "max_seq_no": "681403"
              },
              "num_docs": 681404
            },
            "seq_no": {
              "max_seq_no": 681403,
              "local_checkpoint": 681403,
              "global_checkpoint": 681403
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "2": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 679066,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 486933558
            },
            "indexing": {
              "index_total": 679066,
              "index_time_in_millis": 289002,
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
              "query_total": 63,
              "query_time_in_millis": 154,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2285,
              "total_time_in_millis": 374276,
              "total_docs": 5174643,
              "total_size_in_bytes": 5828513961,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 15255,
              "total_auto_throttle_in_bytes": 14323830
            },
            "refresh": {
              "total": 14159,
              "total_time_in_millis": 643768,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 522
            },
            "warmer": {
              "current": 0,
              "total": 14154,
              "total_time_in_millis": 4492
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 457,
              "hit_count": 0,
              "miss_count": 457,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 19,
              "memory_in_bytes": 1096735,
              "terms_memory_in_bytes": 364967,
              "stored_fields_memory_in_bytes": 202648,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 96964,
              "doc_values_memory_in_bytes": 432156,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108686488
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5,
              "miss_count": 36
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AryL3w==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "679065",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "i5qcBk7yQhSH8jasFexijg",
                "history_uuid": "Rparuq3WRkG1TEK3ygtXrQ",
                "sync_id": "3sk3Ipt9QMKY_7YNxR25pw",
                "translog_generation": "19",
                "max_seq_no": "679065"
              },
              "num_docs": 679066
            },
            "seq_no": {
              "max_seq_no": 679065,
              "local_checkpoint": 679065,
              "global_checkpoint": 679065
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 679066,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 489967290
            },
            "indexing": {
              "index_total": 679066,
              "index_time_in_millis": 306510,
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
              "query_total": 64,
              "query_time_in_millis": 305,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2099,
              "total_time_in_millis": 384015,
              "total_docs": 5027428,
              "total_size_in_bytes": 5617945213,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 13689,
              "total_auto_throttle_in_bytes": 14323830
            },
            "refresh": {
              "total": 14037,
              "total_time_in_millis": 609995,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 390
            },
            "warmer": {
              "current": 0,
              "total": 14032,
              "total_time_in_millis": 4101
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 501,
              "hit_count": 0,
              "miss_count": 501,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 19,
              "memory_in_bytes": 1083944,
              "terms_memory_in_bytes": 365289,
              "stored_fields_memory_in_bytes": 201968,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 99035,
              "doc_values_memory_in_bytes": 417652,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108686507
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 8,
              "miss_count": 33
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGK9lw==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "679065",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "oF25TGNdTB6DKLW4RYyjYw",
                "history_uuid": "Rparuq3WRkG1TEK3ygtXrQ",
                "sync_id": "3sk3Ipt9QMKY_7YNxR25pw",
                "translog_generation": "19",
                "max_seq_no": "679065"
              },
              "num_docs": 679066
            },
            "seq_no": {
              "max_seq_no": 679065,
              "local_checkpoint": 679065,
              "global_checkpoint": 679065
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "3": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 680318,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 487560609
            },
            "indexing": {
              "index_total": 680318,
              "index_time_in_millis": 259834,
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
              "query_total": 58,
              "query_time_in_millis": 403,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2100,
              "total_time_in_millis": 398600,
              "total_docs": 4964975,
              "total_size_in_bytes": 5571678367,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 18985,
              "total_auto_throttle_in_bytes": 13021663
            },
            "refresh": {
              "total": 13998,
              "total_time_in_millis": 581031,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 412
            },
            "warmer": {
              "current": 0,
              "total": 13994,
              "total_time_in_millis": 4845
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 423,
              "hit_count": 0,
              "miss_count": 423,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 22,
              "memory_in_bytes": 1301670,
              "terms_memory_in_bytes": 393394,
              "stored_fields_memory_in_bytes": 202680,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 96132,
              "doc_values_memory_in_bytes": 609464,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672001736,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108686504
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 8,
              "miss_count": 33
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOwqCA==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "680317",
                "max_unsafe_auto_id_timestamp": "1542672001736",
                "translog_uuid": "OpHVKDGNRC6KtHQfAgL9RA",
                "history_uuid": "JY-usqfDTxeUokMcjsgRrA",
                "sync_id": "o2HHWMYpSZ-9B0hj__QjGg",
                "translog_generation": "19",
                "max_seq_no": "680317"
              },
              "num_docs": 680318
            },
            "seq_no": {
              "max_seq_no": 680317,
              "local_checkpoint": 680317,
              "global_checkpoint": 680317
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 680318,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 490116011
            },
            "indexing": {
              "index_total": 680318,
              "index_time_in_millis": 332911,
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
              "query_total": 69,
              "query_time_in_millis": 264,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2320,
              "total_time_in_millis": 374388,
              "total_docs": 5365377,
              "total_size_in_bytes": 5977601874,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 15549,
              "total_auto_throttle_in_bytes": 15756213
            },
            "refresh": {
              "total": 14164,
              "total_time_in_millis": 620505,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 521
            },
            "warmer": {
              "current": 0,
              "total": 14159,
              "total_time_in_millis": 4126
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 346,
              "hit_count": 0,
              "miss_count": 346,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 18,
              "memory_in_bytes": 1222589,
              "terms_memory_in_bytes": 353599,
              "stored_fields_memory_in_bytes": 200352,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 94334,
              "doc_values_memory_in_bytes": 574304,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108686373
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 9,
              "miss_count": 32
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGK9nA==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "680317",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "6dllfkJQQWCk3Si01kdWNA",
                "history_uuid": "JY-usqfDTxeUokMcjsgRrA",
                "sync_id": "o2HHWMYpSZ-9B0hj__QjGg",
                "translog_generation": "19",
                "max_seq_no": "680317"
              },
              "num_docs": 680318
            },
            "seq_no": {
              "max_seq_no": 680317,
              "local_checkpoint": 680317,
              "global_checkpoint": 680317
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "4": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 678937,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 481890479
            },
            "indexing": {
              "index_total": 678937,
              "index_time_in_millis": 296537,
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
              "query_total": 61,
              "query_time_in_millis": 153,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2162,
              "total_time_in_millis": 381302,
              "total_docs": 5415231,
              "total_size_in_bytes": 5933755316,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 20470,
              "total_auto_throttle_in_bytes": 15756213
            },
            "refresh": {
              "total": 14010,
              "total_time_in_millis": 606137,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 329
            },
            "warmer": {
              "current": 0,
              "total": 14005,
              "total_time_in_millis": 4781
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 193,
              "hit_count": 0,
              "miss_count": 193,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 15,
              "memory_in_bytes": 1351008,
              "terms_memory_in_bytes": 313841,
              "stored_fields_memory_in_bytes": 201744,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 88611,
              "doc_values_memory_in_bytes": 746812,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688639
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 6,
              "miss_count": 35
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbOwp/Q==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "678936",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "qHR3hdGmS6WOCMCWjRX_QA",
                "history_uuid": "YjDCK5VATPWV47VIr1inrA",
                "sync_id": "b6zQebSISL6VletgSmRh3g",
                "translog_generation": "19",
                "max_seq_no": "678936"
              },
              "num_docs": 678937
            },
            "seq_no": {
              "max_seq_no": 678936,
              "local_checkpoint": 678936,
              "global_checkpoint": 678936
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 678937,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 485353394
            },
            "indexing": {
              "index_total": 678937,
              "index_time_in_millis": 286968,
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
              "query_total": 66,
              "query_time_in_millis": 1104,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2052,
              "total_time_in_millis": 379694,
              "total_docs": 5013927,
              "total_size_in_bytes": 5590904921,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 15886,
              "total_auto_throttle_in_bytes": 14323830
            },
            "refresh": {
              "total": 13900,
              "total_time_in_millis": 656452,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 340
            },
            "warmer": {
              "current": 0,
              "total": 13895,
              "total_time_in_millis": 4693
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 401,
              "hit_count": 0,
              "miss_count": 401,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 21,
              "memory_in_bytes": 1275604,
              "terms_memory_in_bytes": 381533,
              "stored_fields_memory_in_bytes": 202456,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 94891,
              "doc_values_memory_in_bytes": 596724,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108688468
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 8,
              "miss_count": 33
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUBur1g==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "678936",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "lfS3lnwUQEW8wFbJXoVEUA",
                "history_uuid": "YjDCK5VATPWV47VIr1inrA",
                "sync_id": "b6zQebSISL6VletgSmRh3g",
                "translog_generation": "19",
                "max_seq_no": "678936"
              },
              "num_docs": 678937
            },
            "seq_no": {
              "max_seq_no": 678936,
              "local_checkpoint": 678936,
              "global_checkpoint": 678936
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    "metricbeat-6.5.0-2018.11.21": {
      "uuid": "wfvicEoPQ5uJ0llJJquz9Q",
      "primaries": {
        "docs": {
          "count": 3617812,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 2739165503
        },
        "indexing": {
          "index_total": 3617812,
          "index_time_in_millis": 1575522,
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
          "query_total": 258,
          "query_time_in_millis": 3387,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 12367,
          "total_time_in_millis": 2246292,
          "total_docs": 29595463,
          "total_size_in_bytes": 34525439068,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 107934,
          "total_auto_throttle_in_bytes": 67961245
        },
        "refresh": {
          "total": 84556,
          "total_time_in_millis": 3576711,
          "listeners": 0
        },
        "flush": {
          "total": 15,
          "periodic": 10,
          "total_time_in_millis": 2417
        },
        "warmer": {
          "current": 0,
          "total": 84530,
          "total_time_in_millis": 28833
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 1641,
          "hit_count": 581,
          "miss_count": 1060,
          "cache_size": 0,
          "cache_count": 44,
          "evictions": 44
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 95,
          "memory_in_bytes": 6048087,
          "terms_memory_in_bytes": 1843970,
          "stored_fields_memory_in_bytes": 1071608,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 522817,
          "doc_values_memory_in_bytes": 2609692,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542758403429,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 1010298,
          "size_in_bytes": 1725252533,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 275,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 21,
          "miss_count": 184
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 7235624,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 5469868436
        },
        "indexing": {
          "index_total": 7235624,
          "index_time_in_millis": 3069057,
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
          "query_total": 525,
          "query_time_in_millis": 5701,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 23637,
          "total_time_in_millis": 4480658,
          "total_docs": 59638767,
          "total_size_in_bytes": 68683007336,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 268355,
          "total_auto_throttle_in_bytes": 130927982
        },
        "refresh": {
          "total": 168977,
          "total_time_in_millis": 6948860,
          "listeners": 0
        },
        "flush": {
          "total": 30,
          "periodic": 20,
          "total_time_in_millis": 5424
        },
        "warmer": {
          "current": 0,
          "total": 168923,
          "total_time_in_millis": 59766
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 3611,
          "hit_count": 1258,
          "miss_count": 2353,
          "cache_size": 0,
          "cache_count": 98,
          "evictions": 98
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 189,
          "memory_in_bytes": 12559277,
          "terms_memory_in_bytes": 3651152,
          "stored_fields_memory_in_bytes": 2144584,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 1036793,
          "doc_values_memory_in_bytes": 5726748,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542758403429,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 2020596,
          "size_in_bytes": 3450505066,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 550,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 44,
          "miss_count": 366
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 723147,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 545862149
            },
            "indexing": {
              "index_total": 723147,
              "index_time_in_millis": 316332,
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
              "query_total": 49,
              "query_time_in_millis": 704,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2436,
              "total_time_in_millis": 477443,
              "total_docs": 6030241,
              "total_size_in_bytes": 6974268854,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 24633,
              "total_auto_throttle_in_bytes": 13021663
            },
            "refresh": {
              "total": 16867,
              "total_time_in_millis": 688892,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 233
            },
            "warmer": {
              "current": 0,
              "total": 16862,
              "total_time_in_millis": 4440
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 406,
              "hit_count": 160,
              "miss_count": 246,
              "cache_size": 0,
              "cache_count": 10,
              "evictions": 10
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 15,
              "memory_in_bytes": 1278640,
              "terms_memory_in_bytes": 323527,
              "stored_fields_memory_in_bytes": 213560,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 101845,
              "doc_values_memory_in_bytes": 639708,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 201125,
              "size_in_bytes": 343095269,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41498756
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 41
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO817A==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "723146",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "_-__wzwHTeuS7d4NLdzYcA",
                "history_uuid": "aFyDWy3QTuyxhynXrlwdtw",
                "sync_id": "1zVyUfQXRUGqy_acskFlgQ",
                "translog_generation": "21",
                "max_seq_no": "723146"
              },
              "num_docs": 723147
            },
            "seq_no": {
              "max_seq_no": 723146,
              "local_checkpoint": 723146,
              "global_checkpoint": 723146
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 723147,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 544407134
            },
            "indexing": {
              "index_total": 723147,
              "index_time_in_millis": 302654,
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
              "query_total": 56,
              "query_time_in_millis": 426,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2193,
              "total_time_in_millis": 497140,
              "total_docs": 6403930,
              "total_size_in_bytes": 7096572269,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 45725,
              "total_auto_throttle_in_bytes": 11837876
            },
            "refresh": {
              "total": 16831,
              "total_time_in_millis": 673744,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 346
            },
            "warmer": {
              "current": 0,
              "total": 16825,
              "total_time_in_millis": 7138
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 435,
              "hit_count": 146,
              "miss_count": 289,
              "cache_size": 0,
              "cache_count": 12,
              "evictions": 12
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 17,
              "memory_in_bytes": 1454854,
              "terms_memory_in_bytes": 343804,
              "stored_fields_memory_in_bytes": 212792,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 98606,
              "doc_values_memory_in_bytes": 799652,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 201125,
              "size_in_bytes": 343095269,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41498596
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5,
              "miss_count": 36
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAZAw==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "723146",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "ZCxjcXVQSvW-ZTtGFSoF-Q",
                "history_uuid": "aFyDWy3QTuyxhynXrlwdtw",
                "sync_id": "1zVyUfQXRUGqy_acskFlgQ",
                "translog_generation": "21",
                "max_seq_no": "723146"
              },
              "num_docs": 723147
            },
            "seq_no": {
              "max_seq_no": 723146,
              "local_checkpoint": 723146,
              "global_checkpoint": 723146
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "1": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 724105,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 549751632
            },
            "indexing": {
              "index_total": 724105,
              "index_time_in_millis": 312151,
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
              "query_total": 52,
              "query_time_in_millis": 782,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2536,
              "total_time_in_millis": 452696,
              "total_docs": 5889894,
              "total_size_in_bytes": 6914259255,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 18404,
              "total_auto_throttle_in_bytes": 15756213
            },
            "refresh": {
              "total": 16985,
              "total_time_in_millis": 762541,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 404
            },
            "warmer": {
              "current": 0,
              "total": 16980,
              "total_time_in_millis": 7707
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 341,
              "hit_count": 114,
              "miss_count": 227,
              "cache_size": 0,
              "cache_count": 10,
              "evictions": 10
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 22,
              "memory_in_bytes": 1380872,
              "terms_memory_in_bytes": 396618,
              "stored_fields_memory_in_bytes": 214392,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 102390,
              "doc_values_memory_in_bytes": 667472,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 203244,
              "size_in_bytes": 346919572,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41737251
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 7,
              "miss_count": 34
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB63HA==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "724104",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "f6eQHqyKQaGjrxUXAAyk5g",
                "history_uuid": "ynkuhdIFSzGo7B4LeadLZw",
                "sync_id": "lqVDblZzTAe3XaeobmtE2A",
                "translog_generation": "21",
                "max_seq_no": "724104"
              },
              "num_docs": 724105
            },
            "seq_no": {
              "max_seq_no": 724104,
              "local_checkpoint": 724104,
              "global_checkpoint": 724104
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 724105,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 549495848
            },
            "indexing": {
              "index_total": 724105,
              "index_time_in_millis": 314796,
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
              "query_total": 53,
              "query_time_in_millis": 318,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2297,
              "total_time_in_millis": 448363,
              "total_docs": 5757543,
              "total_size_in_bytes": 6671087367,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 21380,
              "total_auto_throttle_in_bytes": 13021663
            },
            "refresh": {
              "total": 16963,
              "total_time_in_millis": 693082,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 389
            },
            "warmer": {
              "current": 0,
              "total": 16957,
              "total_time_in_millis": 4263
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 327,
              "hit_count": 125,
              "miss_count": 202,
              "cache_size": 0,
              "cache_count": 10,
              "evictions": 10
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 21,
              "memory_in_bytes": 1246367,
              "terms_memory_in_bytes": 380926,
              "stored_fields_memory_in_bytes": 215392,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 106677,
              "doc_values_memory_in_bytes": 543372,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 203244,
              "size_in_bytes": 346919572,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41737273
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 8,
              "miss_count": 33
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGZllA==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "724104",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "uY8NG9G9TEqbIwRtkKyeMQ",
                "history_uuid": "ynkuhdIFSzGo7B4LeadLZw",
                "sync_id": "lqVDblZzTAe3XaeobmtE2A",
                "translog_generation": "21",
                "max_seq_no": "724104"
              },
              "num_docs": 724105
            },
            "seq_no": {
              "max_seq_no": 724104,
              "local_checkpoint": 724104,
              "global_checkpoint": 724104
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "2": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 722865,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 540566484
            },
            "indexing": {
              "index_total": 722865,
              "index_time_in_millis": 294793,
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
              "query_total": 53,
              "query_time_in_millis": 528,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2292,
              "total_time_in_millis": 441975,
              "total_docs": 6341657,
              "total_size_in_bytes": 7088542438,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 45441,
              "total_auto_throttle_in_bytes": 13021663
            },
            "refresh": {
              "total": 16961,
              "total_time_in_millis": 682330,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 385
            },
            "warmer": {
              "current": 0,
              "total": 16956,
              "total_time_in_millis": 7856
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 444,
              "hit_count": 149,
              "miss_count": 295,
              "cache_size": 0,
              "cache_count": 12,
              "evictions": 12
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 16,
              "memory_in_bytes": 1451909,
              "terms_memory_in_bytes": 323949,
              "stored_fields_memory_in_bytes": 214680,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 94832,
              "doc_values_memory_in_bytes": 818448,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 200587,
              "size_in_bytes": 341918086,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41528622
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5,
              "miss_count": 36
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB63Fg==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "722864",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "xDMCMUfHRXyQ6n29SPt6Xg",
                "history_uuid": "ycB3LEFzRwuGCmATUAhQ8g",
                "sync_id": "iQH89OTPTW2xjRvwJwxkrg",
                "translog_generation": "21",
                "max_seq_no": "722864"
              },
              "num_docs": 722865
            },
            "seq_no": {
              "max_seq_no": 722864,
              "local_checkpoint": 722864,
              "global_checkpoint": 722864
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 722865,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 546614217
            },
            "indexing": {
              "index_total": 722865,
              "index_time_in_millis": 308132,
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
              "query_total": 52,
              "query_time_in_millis": 789,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2476,
              "total_time_in_millis": 460138,
              "total_docs": 6033668,
              "total_size_in_bytes": 6985579975,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 19840,
              "total_auto_throttle_in_bytes": 13021663
            },
            "refresh": {
              "total": 16849,
              "total_time_in_millis": 717555,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 468
            },
            "warmer": {
              "current": 0,
              "total": 16843,
              "total_time_in_millis": 7547
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 299,
              "hit_count": 98,
              "miss_count": 201,
              "cache_size": 0,
              "cache_count": 8,
              "evictions": 8
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 22,
              "memory_in_bytes": 1210097,
              "terms_memory_in_bytes": 406865,
              "stored_fields_memory_in_bytes": 215048,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 106832,
              "doc_values_memory_in_bytes": 481352,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 200587,
              "size_in_bytes": 341918086,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41528644
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 6,
              "miss_count": 35
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAZCA==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "722864",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "3m47uVhVQkOTwh74ivic6A",
                "history_uuid": "ycB3LEFzRwuGCmATUAhQ8g",
                "sync_id": "iQH89OTPTW2xjRvwJwxkrg",
                "translog_generation": "21",
                "max_seq_no": "722864"
              },
              "num_docs": 722865
            },
            "seq_no": {
              "max_seq_no": 722864,
              "local_checkpoint": 722864,
              "global_checkpoint": 722864
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "3": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 723731,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 548002674
            },
            "indexing": {
              "index_total": 723731,
              "index_time_in_millis": 275571,
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
              "query_total": 49,
              "query_time_in_millis": 603,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2277,
              "total_time_in_millis": 442002,
              "total_docs": 5736430,
              "total_size_in_bytes": 6639400693,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 30428,
              "total_auto_throttle_in_bytes": 10761705
            },
            "refresh": {
              "total": 16843,
              "total_time_in_millis": 636246,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 259
            },
            "warmer": {
              "current": 0,
              "total": 16837,
              "total_time_in_millis": 4335
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 257,
              "hit_count": 87,
              "miss_count": 170,
              "cache_size": 0,
              "cache_count": 6,
              "evictions": 6
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 19,
              "memory_in_bytes": 1211633,
              "terms_memory_in_bytes": 367051,
              "stored_fields_memory_in_bytes": 213984,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 106122,
              "doc_values_memory_in_bytes": 524476,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 202987,
              "size_in_bytes": 347122803,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41807389
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 41
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO817g==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "723730",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "IftmT24cRH6Xyg2Bs4AbdA",
                "history_uuid": "biWTihhDSWG-3HkTUIoNnA",
                "sync_id": "pJVUAAQkRSS_NgUlEWVbGA",
                "translog_generation": "21",
                "max_seq_no": "723730"
              },
              "num_docs": 723731
            },
            "seq_no": {
              "max_seq_no": 723730,
              "local_checkpoint": 723730,
              "global_checkpoint": 723730
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 723731,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 548714582
            },
            "indexing": {
              "index_total": 723731,
              "index_time_in_millis": 333752,
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
              "query_total": 56,
              "query_time_in_millis": 355,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2526,
              "total_time_in_millis": 442558,
              "total_docs": 5832620,
              "total_size_in_bytes": 6874986648,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 27230,
              "total_auto_throttle_in_bytes": 11837876
            },
            "refresh": {
              "total": 16987,
              "total_time_in_millis": 734111,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 845
            },
            "warmer": {
              "current": 0,
              "total": 16982,
              "total_time_in_millis": 4415
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 335,
              "hit_count": 114,
              "miss_count": 221,
              "cache_size": 0,
              "cache_count": 10,
              "evictions": 10
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 16,
              "memory_in_bytes": 1121452,
              "terms_memory_in_bytes": 325691,
              "stored_fields_memory_in_bytes": 213824,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 104873,
              "doc_values_memory_in_bytes": 477064,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 202987,
              "size_in_bytes": 347122803,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41807296
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 8,
              "miss_count": 33
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGZliQ==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "723730",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "aSY-69MBQmGzjRXP_jerdg",
                "history_uuid": "biWTihhDSWG-3HkTUIoNnA",
                "sync_id": "pJVUAAQkRSS_NgUlEWVbGA",
                "translog_generation": "21",
                "max_seq_no": "723730"
              },
              "num_docs": 723731
            },
            "seq_no": {
              "max_seq_no": 723730,
              "local_checkpoint": 723730,
              "global_checkpoint": 723730
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "4": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 723964,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 548222923
            },
            "indexing": {
              "index_total": 723964,
              "index_time_in_millis": 305155,
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
              "query_total": 49,
              "query_time_in_millis": 757,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2393,
              "total_time_in_millis": 413457,
              "total_docs": 5809040,
              "total_size_in_bytes": 6776344336,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 17827,
              "total_auto_throttle_in_bytes": 14323830
            },
            "refresh": {
              "total": 16868,
              "total_time_in_millis": 673612,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 467
            },
            "warmer": {
              "current": 0,
              "total": 16863,
              "total_time_in_millis": 4724
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 260,
              "hit_count": 95,
              "miss_count": 165,
              "cache_size": 0,
              "cache_count": 6,
              "evictions": 6
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 20,
              "memory_in_bytes": 1057026,
              "terms_memory_in_bytes": 391269,
              "stored_fields_memory_in_bytes": 214784,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 106877,
              "doc_values_memory_in_bytes": 344096,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 202355,
              "size_in_bytes": 346196803,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41690248
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 41
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO816w==",
              "generation": 6,
              "user_data": {
                "local_checkpoint": "723963",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "PmGrMpYaRvaVXN444BMG_A",
                "history_uuid": "U1iB-HVbT5GXllsbRlmwcw",
                "sync_id": "1HR7-Nx_TYSTlMZNJMBhvw",
                "translog_generation": "21",
                "max_seq_no": "723963"
              },
              "num_docs": 723964
            },
            "seq_no": {
              "max_seq_no": 723963,
              "local_checkpoint": 723963,
              "global_checkpoint": 723963
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 723964,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 548230793
            },
            "indexing": {
              "index_total": 723964,
              "index_time_in_millis": 305721,
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
              "query_total": 56,
              "query_time_in_millis": 439,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2211,
              "total_time_in_millis": 404886,
              "total_docs": 5803744,
              "total_size_in_bytes": 6661965501,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 17447,
              "total_auto_throttle_in_bytes": 14323830
            },
            "refresh": {
              "total": 16823,
              "total_time_in_millis": 686747,
              "listeners": 0
            },
            "flush": {
              "total": 3,
              "periodic": 2,
              "total_time_in_millis": 1628
            },
            "warmer": {
              "current": 0,
              "total": 16818,
              "total_time_in_millis": 7341
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 507,
              "hit_count": 170,
              "miss_count": 337,
              "cache_size": 0,
              "cache_count": 14,
              "evictions": 14
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 21,
              "memory_in_bytes": 1146427,
              "terms_memory_in_bytes": 391452,
              "stored_fields_memory_in_bytes": 216128,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 107739,
              "doc_values_memory_in_bytes": 431108,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542758403429,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 202355,
              "size_in_bytes": 346196803,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 41689968
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 5,
              "miss_count": 36
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAZAg==",
              "generation": 7,
              "user_data": {
                "local_checkpoint": "723963",
                "max_unsafe_auto_id_timestamp": "1542758403429",
                "translog_uuid": "-J1qiZyJTjCJ45MaRP1enw",
                "history_uuid": "U1iB-HVbT5GXllsbRlmwcw",
                "sync_id": "1HR7-Nx_TYSTlMZNJMBhvw",
                "translog_generation": "21",
                "max_seq_no": "723963"
              },
              "num_docs": 723964
            },
            "seq_no": {
              "max_seq_no": 723963,
              "local_checkpoint": 723963,
              "global_checkpoint": 723963
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    "metricbeat-6.5.0-2018.11.22": {
      "uuid": "if8YZ-q4Qqyz8Htgf3aDsQ",
      "primaries": {
        "docs": {
          "count": 961008,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 786722318
        },
        "indexing": {
          "index_total": 961058,
          "index_time_in_millis": 417141,
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
          "query_total": 44,
          "query_time_in_millis": 0,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 3140,
          "total_time_in_millis": 599500,
          "total_docs": 9218887,
          "total_size_in_bytes": 10424683859,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 10194,
          "total_auto_throttle_in_bytes": 99138094
        },
        "refresh": {
          "total": 21764,
          "total_time_in_millis": 954646,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 59
        },
        "warmer": {
          "current": 0,
          "total": 21755,
          "total_time_in_millis": 11516
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 65,
          "memory_in_bytes": 3334764,
          "terms_memory_in_bytes": 1023259,
          "stored_fields_memory_in_bytes": 293312,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 163301,
          "doc_values_memory_in_bytes": 1854892,
          "index_writer_memory_in_bytes": 42870288,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 961058,
          "size_in_bytes": 1641648764,
          "uncommitted_operations": 669456,
          "uncommitted_size_in_bytes": 1143851849,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 1921995,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 1572243456
        },
        "indexing": {
          "index_total": 1514840,
          "index_time_in_millis": 654663,
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
          "query_total": 104,
          "query_time_in_millis": 0,
          "query_current": 0,
          "fetch_total": 0,
          "fetch_time_in_millis": 0,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 4722,
          "total_time_in_millis": 906385,
          "total_docs": 13684969,
          "total_size_in_bytes": 15600541328,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 12641,
          "total_auto_throttle_in_bytes": 202089192
        },
        "refresh": {
          "total": 34171,
          "total_time_in_millis": 1485572,
          "listeners": 0
        },
        "flush": {
          "total": 5,
          "periodic": 1,
          "total_time_in_millis": 303
        },
        "warmer": {
          "current": 0,
          "total": 34158,
          "total_time_in_millis": 18600
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 135,
          "memory_in_bytes": 6878790,
          "terms_memory_in_bytes": 2101630,
          "stored_fields_memory_in_bytes": 585688,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 332012,
          "doc_values_memory_in_bytes": 3859460,
          "index_writer_memory_in_bytes": 73395576,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542862101307,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 2070991,
          "size_in_bytes": 3538652674,
          "uncommitted_operations": 1220698,
          "uncommitted_size_in_bytes": 2084944152,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 185567,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 168945121
            },
            "indexing": {
              "index_total": 185574,
              "index_time_in_millis": 78268,
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
              "query_total": 6,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 597,
              "total_time_in_millis": 118366,
              "total_docs": 1854234,
              "total_size_in_bytes": 2060367319,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 4251,
              "total_time_in_millis": 175072,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 31
            },
            "warmer": {
              "current": 0,
              "total": 4248,
              "total_time_in_millis": 1659
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 16,
              "memory_in_bytes": 727477,
              "terms_memory_in_bytes": 242135,
              "stored_fields_memory_in_bytes": 57328,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 34014,
              "doc_values_memory_in_bytes": 394000,
              "index_writer_memory_in_bytes": 9071000,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 185574,
              "size_in_bytes": 316366635,
              "uncommitted_operations": 39835,
              "uncommitted_size_in_bytes": 68441078,
              "earliest_last_modified_age": 22588019
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO/GIQ==",
              "generation": 4,
              "user_data": {
                "local_checkpoint": "145738",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "WjziZ2xfRUWAqKd1Si7M5w",
                "history_uuid": "0MOB_9IdQ5agySuCuMH_7w",
                "sync_id": "7xP276TCQoKdhx71wrqvFA",
                "translog_generation": "6",
                "max_seq_no": "145738"
              },
              "num_docs": 145739
            },
            "seq_no": {
              "max_seq_no": 185573,
              "local_checkpoint": 185573,
              "global_checkpoint": 185566
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 185567,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 152995210
            },
            "indexing": {
              "index_total": 47037,
              "index_time_in_millis": 20911,
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
              "query_total": 16,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 134,
              "total_time_in_millis": 22965,
              "total_docs": 246020,
              "total_size_in_bytes": 331519921,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 1061,
              "total_time_in_millis": 44558,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 65
            },
            "warmer": {
              "current": 0,
              "total": 1060,
              "total_time_in_millis": 641
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 13,
              "memory_in_bytes": 710455,
              "terms_memory_in_bytes": 194630,
              "stored_fields_memory_in_bytes": 55952,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 31749,
              "doc_values_memory_in_bytes": 428124,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542861071320,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 185567,
              "size_in_bytes": 316356795,
              "uncommitted_operations": 39828,
              "uncommitted_size_in_bytes": 68431238,
              "earliest_last_modified_age": 6317996
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB9Plw==",
              "generation": 5,
              "user_data": {
                "local_checkpoint": "145738",
                "max_unsafe_auto_id_timestamp": "1542861071320",
                "translog_uuid": "FBVdSrmPQOaHr6p36wXeMw",
                "history_uuid": "0MOB_9IdQ5agySuCuMH_7w",
                "sync_id": "7xP276TCQoKdhx71wrqvFA",
                "translog_generation": "6",
                "max_seq_no": "145738"
              },
              "num_docs": 145739
            },
            "seq_no": {
              "max_seq_no": 185566,
              "local_checkpoint": 185566,
              "global_checkpoint": 185566
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "1": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 196836,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 151521595
            },
            "indexing": {
              "index_total": 196842,
              "index_time_in_millis": 86947,
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
              "query_total": 11,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 648,
              "total_time_in_millis": 136588,
              "total_docs": 2037416,
              "total_size_in_bytes": 2255020224,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 5659,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 4400,
              "total_time_in_millis": 207455,
              "listeners": 0
            },
            "flush": {
              "total": 0,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 4399,
              "total_time_in_millis": 2593
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 10,
              "memory_in_bytes": 477272,
              "terms_memory_in_bytes": 166328,
              "stored_fields_memory_in_bytes": 59664,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 30120,
              "doc_values_memory_in_bytes": 221160,
              "index_writer_memory_in_bytes": 8125056,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 196842,
              "size_in_bytes": 335412722,
              "uncommitted_operations": 196842,
              "uncommitted_size_in_bytes": 335412722,
              "earliest_last_modified_age": 22587926
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB60Wg==",
              "generation": 2,
              "user_data": {
                "local_checkpoint": "-1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "v_tcXY5ETgyIOy1NJTMErg",
                "history_uuid": "FqC8laJISIi7Qyl53NZq0Q",
                "translog_generation": "1",
                "max_seq_no": "-1"
              },
              "num_docs": 0
            },
            "seq_no": {
              "max_seq_no": 196841,
              "local_checkpoint": 196841,
              "global_checkpoint": 196841
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 196825,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 156672765
            },
            "indexing": {
              "index_total": 196842,
              "index_time_in_millis": 83307,
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
              "query_total": 11,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 561,
              "total_time_in_millis": 119657,
              "total_docs": 1799232,
              "total_size_in_bytes": 2011415186,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 4422,
              "total_time_in_millis": 185805,
              "listeners": 0
            },
            "flush": {
              "total": 0,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 4421,
              "total_time_in_millis": 2274
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 14,
              "memory_in_bytes": 678770,
              "terms_memory_in_bytes": 221630,
              "stored_fields_memory_in_bytes": 59128,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 35372,
              "doc_values_memory_in_bytes": 362640,
              "index_writer_memory_in_bytes": 10520776,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 196842,
              "size_in_bytes": 335412722,
              "uncommitted_operations": 196842,
              "uncommitted_size_in_bytes": 335412722,
              "earliest_last_modified_age": 22587768
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAVyw==",
              "generation": 3,
              "user_data": {
                "local_checkpoint": "-1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "kUNAAHh5Qx60udKymH-s_g",
                "history_uuid": "FqC8laJISIi7Qyl53NZq0Q",
                "translog_generation": "1",
                "max_seq_no": "-1"
              },
              "num_docs": 0
            },
            "seq_no": {
              "max_seq_no": 196841,
              "local_checkpoint": 196841,
              "global_checkpoint": 196841
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "2": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 196960,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 159346905
            },
            "indexing": {
              "index_total": 196979,
              "index_time_in_millis": 86375,
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
              "query_total": 12,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 644,
              "total_time_in_millis": 123901,
              "total_docs": 1784064,
              "total_size_in_bytes": 2054056203,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 2624,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 4422,
              "total_time_in_millis": 203986,
              "listeners": 0
            },
            "flush": {
              "total": 0,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 4421,
              "total_time_in_millis": 2804
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 11,
              "memory_in_bytes": 733020,
              "terms_memory_in_bytes": 177681,
              "stored_fields_memory_in_bytes": 59656,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 32607,
              "doc_values_memory_in_bytes": 463076,
              "index_writer_memory_in_bytes": 8711152,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 196979,
              "size_in_bytes": 336952707,
              "uncommitted_operations": 196979,
              "uncommitted_size_in_bytes": 336952707,
              "earliest_last_modified_age": 22587948
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAVyg==",
              "generation": 2,
              "user_data": {
                "local_checkpoint": "-1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "3wyUSIeZQPCLkP99gEKKbw",
                "history_uuid": "ZWkTPu3-SpSGnCQGq9JcXA",
                "translog_generation": "1",
                "max_seq_no": "-1"
              },
              "num_docs": 0
            },
            "seq_no": {
              "max_seq_no": 196978,
              "local_checkpoint": 196978,
              "global_checkpoint": 149969
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 196959,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 169632585
            },
            "indexing": {
              "index_total": 47974,
              "index_time_in_millis": 20953,
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
              "query_total": 4,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 131,
              "total_time_in_millis": 19945,
              "total_docs": 252525,
              "total_size_in_bytes": 331487357,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 1035,
              "total_time_in_millis": 40416,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 1,
              "total_time_in_millis": 146
            },
            "warmer": {
              "current": 0,
              "total": 1035,
              "total_time_in_millis": 691
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 11,
              "memory_in_bytes": 686270,
              "terms_memory_in_bytes": 185461,
              "stored_fields_memory_in_bytes": 59488,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 32901,
              "doc_values_memory_in_bytes": 408420,
              "index_writer_memory_in_bytes": 8533488,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542862101307,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 345869,
              "size_in_bytes": 592328134,
              "uncommitted_operations": 78780,
              "uncommitted_size_in_bytes": 134213442,
              "earliest_last_modified_age": 7258531
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGcm4g==",
              "generation": 4,
              "user_data": {
                "local_checkpoint": "149969",
                "max_unsafe_auto_id_timestamp": "1542862101307",
                "translog_uuid": "uWoweTULQ2mfQorweSuiGA",
                "history_uuid": "ZWkTPu3-SpSGnCQGq9JcXA",
                "translog_generation": "9",
                "max_seq_no": "164414"
              },
              "num_docs": 164404
            },
            "seq_no": {
              "max_seq_no": 196978,
              "local_checkpoint": 149969,
              "global_checkpoint": 149969
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "3": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 196377,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 156255583
            },
            "indexing": {
              "index_total": 76670,
              "index_time_in_millis": 32578,
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
              "query_total": 13,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 209,
              "total_time_in_millis": 36343,
              "total_docs": 529909,
              "total_size_in_bytes": 639502313,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 1657,
              "total_time_in_millis": 73632,
              "listeners": 0
            },
            "flush": {
              "total": 0,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1658,
              "total_time_in_millis": 918
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 15,
              "memory_in_bytes": 739788,
              "terms_memory_in_bytes": 228772,
              "stored_fields_memory_in_bytes": 60128,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 34116,
              "doc_values_memory_in_bytes": 416772,
              "index_writer_memory_in_bytes": 11471024,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542858849367,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 196396,
              "size_in_bytes": 335412886,
              "uncommitted_operations": 196396,
              "uncommitted_size_in_bytes": 335412886,
              "earliest_last_modified_age": 8539163
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsCmYg==",
              "generation": 3,
              "user_data": {
                "local_checkpoint": "-1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "ybnqcdJpTPuI0pYZT4mY_w",
                "history_uuid": "4bjzlZHcRXO8_Ttn4RvqTA",
                "translog_generation": "1",
                "max_seq_no": "-1"
              },
              "num_docs": 0
            },
            "seq_no": {
              "max_seq_no": 196395,
              "local_checkpoint": 196395,
              "global_checkpoint": 196395
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 196386,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 156266451
            },
            "indexing": {
              "index_total": 196396,
              "index_time_in_millis": 84925,
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
              "query_total": 9,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 649,
              "total_time_in_millis": 115799,
              "total_docs": 1838404,
              "total_size_in_bytes": 2102711035,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 4439,
              "total_time_in_millis": 194939,
              "listeners": 0
            },
            "flush": {
              "total": 0,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 4438,
              "total_time_in_millis": 3003
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 11,
              "memory_in_bytes": 669679,
              "terms_memory_in_bytes": 189336,
              "stored_fields_memory_in_bytes": 58864,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 34203,
              "doc_values_memory_in_bytes": 387276,
              "index_writer_memory_in_bytes": 8940488,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 196396,
              "size_in_bytes": 335412886,
              "uncommitted_operations": 196396,
              "uncommitted_size_in_bytes": 335412886,
              "earliest_last_modified_age": 22587810
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGZiQQ==",
              "generation": 2,
              "user_data": {
                "local_checkpoint": "-1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "KczKsu6xRkeLda8pkQQTTg",
                "history_uuid": "4bjzlZHcRXO8_Ttn4RvqTA",
                "translog_generation": "1",
                "max_seq_no": "-1"
              },
              "num_docs": 0
            },
            "seq_no": {
              "max_seq_no": 196395,
              "local_checkpoint": 196395,
              "global_checkpoint": 196395
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ],
        "4": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "AKGUBPhiRBeSdwhI_zecGQ",
              "relocating_node": null
            },
            "docs": {
              "count": 185259,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 150642246
            },
            "indexing": {
              "index_total": 185267,
              "index_time_in_millis": 80626,
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
              "query_total": 6,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 602,
              "total_time_in_millis": 104846,
              "total_docs": 1704769,
              "total_size_in_bytes": 1952529078,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 1911,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 4252,
              "total_time_in_millis": 173194,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 28
            },
            "warmer": {
              "current": 0,
              "total": 4249,
              "total_time_in_millis": 1457
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 17,
              "memory_in_bytes": 727316,
              "terms_memory_in_bytes": 247779,
              "stored_fields_memory_in_bytes": 57800,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 32357,
              "doc_values_memory_in_bytes": 389380,
              "index_writer_memory_in_bytes": 8022592,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 185267,
              "size_in_bytes": 317503814,
              "uncommitted_operations": 39404,
              "uncommitted_size_in_bytes": 67632456,
              "earliest_last_modified_age": 22588027
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "GWW9DN5so66jm1SDbO/GKQ==",
              "generation": 4,
              "user_data": {
                "local_checkpoint": "145862",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "FNusM06rRW6VJ1GZ-Jomkg",
                "history_uuid": "Wi_sAJHHTY-y2gAWIcliiQ",
                "sync_id": "JHyVHzbxQ--k4Xg3ijDaMw",
                "translog_generation": "6",
                "max_seq_no": "145862"
              },
              "num_docs": 145863
            },
            "seq_no": {
              "max_seq_no": 185266,
              "local_checkpoint": 185266,
              "global_checkpoint": 185258
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 185259,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 149964995
            },
            "indexing": {
              "index_total": 185259,
              "index_time_in_millis": 79773,
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
              "query_total": 16,
              "query_time_in_millis": 0,
              "query_current": 0,
              "fetch_total": 0,
              "fetch_time_in_millis": 0,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 547,
              "total_time_in_millis": 107975,
              "total_docs": 1638396,
              "total_size_in_bytes": 1861932692,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 2447,
              "total_auto_throttle_in_bytes": 19065018
            },
            "refresh": {
              "total": 4232,
              "total_time_in_millis": 186515,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 33
            },
            "warmer": {
              "current": 0,
              "total": 4229,
              "total_time_in_millis": 2560
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 17,
              "memory_in_bytes": 728743,
              "terms_memory_in_bytes": 247878,
              "stored_fields_memory_in_bytes": 57680,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 34573,
              "doc_values_memory_in_bytes": 388612,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 185259,
              "size_in_bytes": 317493373,
              "uncommitted_operations": 39396,
              "uncommitted_size_in_bytes": 67622015,
              "earliest_last_modified_age": 22587746
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB9Ppg==",
              "generation": 5,
              "user_data": {
                "local_checkpoint": "145862",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "7sYfshm6SpmY-cqgFFUacQ",
                "history_uuid": "Wi_sAJHHTY-y2gAWIcliiQ",
                "sync_id": "JHyVHzbxQ--k4Xg3ijDaMw",
                "translog_generation": "6",
                "max_seq_no": "145862"
              },
              "num_docs": 145863
            },
            "seq_no": {
              "max_seq_no": 185258,
              "local_checkpoint": 185258,
              "global_checkpoint": 185258
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-beats-6-2018.11.22": {
      "uuid": "qOD9VfqMSkiitv_wcPBkJQ",
      "primaries": {
        "docs": {
          "count": 10444,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 7297990
        },
        "indexing": {
          "index_total": 10444,
          "index_time_in_millis": 18127,
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
          "query_total": 11,
          "query_time_in_millis": 3,
          "query_current": 0,
          "fetch_total": 1,
          "fetch_time_in_millis": 3,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 587,
          "total_time_in_millis": 86924,
          "total_docs": 1072601,
          "total_size_in_bytes": 893293905,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 5532,
          "total_time_in_millis": 87914,
          "listeners": 0
        },
        "flush": {
          "total": 0,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 5531,
          "total_time_in_millis": 540
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 11,
          "memory_in_bytes": 68581,
          "terms_memory_in_bytes": 52985,
          "stored_fields_memory_in_bytes": 3920,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 3712,
          "doc_values_memory_in_bytes": 7964,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542844800738,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 10444,
          "size_in_bytes": 14054292,
          "uncommitted_operations": 10444,
          "uncommitted_size_in_bytes": 14054292,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 20888,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 14619009
        },
        "indexing": {
          "index_total": 13785,
          "index_time_in_millis": 24535,
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
          "query_total": 24,
          "query_time_in_millis": 6,
          "query_current": 0,
          "fetch_total": 2,
          "fetch_time_in_millis": 28,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 775,
          "total_time_in_millis": 110583,
          "total_docs": 1381413,
          "total_size_in_bytes": 1161728707,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 7341,
          "total_time_in_millis": 115521,
          "listeners": 0
        },
        "flush": {
          "total": 0,
          "periodic": 0,
          "total_time_in_millis": 0
        },
        "warmer": {
          "current": 0,
          "total": 7340,
          "total_time_in_millis": 693
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 0,
          "hit_count": 0,
          "miss_count": 0,
          "cache_size": 0,
          "cache_count": 0,
          "evictions": 0
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 21,
          "memory_in_bytes": 139278,
          "terms_memory_in_bytes": 106518,
          "stored_fields_memory_in_bytes": 7512,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 7412,
          "doc_values_memory_in_bytes": 17836,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542860012163,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 20888,
          "size_in_bytes": 28108584,
          "uncommitted_operations": 20888,
          "uncommitted_size_in_bytes": 28108584,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 0,
          "miss_count": 0
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 10444,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 7321019
            },
            "indexing": {
              "index_total": 3341,
              "index_time_in_millis": 6408,
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
              "query_total": 13,
              "query_time_in_millis": 3,
              "query_current": 0,
              "fetch_total": 1,
              "fetch_time_in_millis": 25,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 188,
              "total_time_in_millis": 23659,
              "total_docs": 308812,
              "total_size_in_bytes": 268434802,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 1809,
              "total_time_in_millis": 27607,
              "listeners": 0
            },
            "flush": {
              "total": 0,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 1809,
              "total_time_in_millis": 153
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 10,
              "memory_in_bytes": 70697,
              "terms_memory_in_bytes": 53533,
              "stored_fields_memory_in_bytes": 3592,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3700,
              "doc_values_memory_in_bytes": 9872,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542860012163,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 10444,
              "size_in_bytes": 14054292,
              "uncommitted_operations": 10444,
              "uncommitted_size_in_bytes": 14054292,
              "earliest_last_modified_age": 7376482
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB83lw==",
              "generation": 3,
              "user_data": {
                "local_checkpoint": "-1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "pf5cx_-oQvCut_C3lVdFQA",
                "history_uuid": "0mNdjGLeS1-rgxASGoElOQ",
                "translog_generation": "1",
                "max_seq_no": "-1"
              },
              "num_docs": 0
            },
            "seq_no": {
              "max_seq_no": 10443,
              "local_checkpoint": 10443,
              "global_checkpoint": 10443
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 10444,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 7297990
            },
            "indexing": {
              "index_total": 10444,
              "index_time_in_millis": 18127,
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
              "query_total": 11,
              "query_time_in_millis": 3,
              "query_current": 0,
              "fetch_total": 1,
              "fetch_time_in_millis": 3,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 587,
              "total_time_in_millis": 86924,
              "total_docs": 1072601,
              "total_size_in_bytes": 893293905,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 5532,
              "total_time_in_millis": 87914,
              "listeners": 0
            },
            "flush": {
              "total": 0,
              "periodic": 0,
              "total_time_in_millis": 0
            },
            "warmer": {
              "current": 0,
              "total": 5531,
              "total_time_in_millis": 540
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 0,
              "hit_count": 0,
              "miss_count": 0,
              "cache_size": 0,
              "cache_count": 0,
              "evictions": 0
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 11,
              "memory_in_bytes": 68581,
              "terms_memory_in_bytes": 52985,
              "stored_fields_memory_in_bytes": 3920,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 3712,
              "doc_values_memory_in_bytes": 7964,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542844800738,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 10444,
              "size_in_bytes": 14054292,
              "uncommitted_operations": 10444,
              "uncommitted_size_in_bytes": 14054292,
              "earliest_last_modified_age": 22588749
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 0,
              "miss_count": 0
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AsAVww==",
              "generation": 2,
              "user_data": {
                "local_checkpoint": "-1",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "VI2wdJjpTgOx935MHbmqBQ",
                "history_uuid": "0mNdjGLeS1-rgxASGoElOQ",
                "translog_generation": "1",
                "max_seq_no": "-1"
              },
              "num_docs": 0
            },
            "seq_no": {
              "max_seq_no": 10443,
              "local_checkpoint": 10443,
              "global_checkpoint": 10443
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-beats-6-2018.11.21": {
      "uuid": "bqnF5QD8SpW5M8eXRbARtA",
      "primaries": {
        "docs": {
          "count": 46368,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 29300129
        },
        "indexing": {
          "index_total": 46368,
          "index_time_in_millis": 78769,
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
          "query_total": 84,
          "query_time_in_millis": 209,
          "query_current": 0,
          "fetch_total": 2,
          "fetch_time_in_millis": 1,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 2458,
          "total_time_in_millis": 537479,
          "total_docs": 9843016,
          "total_size_in_bytes": 7217295434,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 23106,
          "total_time_in_millis": 376567,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 28
        },
        "warmer": {
          "current": 0,
          "total": 23103,
          "total_time_in_millis": 1472
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 347,
          "hit_count": 103,
          "miss_count": 244,
          "cache_size": 0,
          "cache_count": 3,
          "evictions": 3
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 3,
          "memory_in_bytes": 47671,
          "terms_memory_in_bytes": 30964,
          "stored_fields_memory_in_bytes": 3728,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 12447,
          "doc_values_memory_in_bytes": 532,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 46368,
          "size_in_bytes": 62383671,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 55,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 1,
          "miss_count": 39
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 92736,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 58738821
        },
        "indexing": {
          "index_total": 92736,
          "index_time_in_millis": 151412,
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
          "query_total": 167,
          "query_time_in_millis": 596,
          "query_current": 0,
          "fetch_total": 4,
          "fetch_time_in_millis": 3,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 4906,
          "total_time_in_millis": 1102418,
          "total_docs": 19716902,
          "total_size_in_bytes": 14452290151,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 46189,
          "total_time_in_millis": 751922,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 56
        },
        "warmer": {
          "current": 0,
          "total": 46183,
          "total_time_in_millis": 2716
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 683,
          "hit_count": 197,
          "miss_count": 486,
          "cache_size": 0,
          "cache_count": 6,
          "evictions": 6
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 12,
          "memory_in_bytes": 123869,
          "terms_memory_in_bytes": 86152,
          "stored_fields_memory_in_bytes": 9440,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 25469,
          "doc_values_memory_in_bytes": 2808,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": -1,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 92736,
          "size_in_bytes": 124767342,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 3,
          "miss_count": 89
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "KmbJ-gnWTCO7I5oemlQIgw",
              "relocating_node": null
            },
            "docs": {
              "count": 46368,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 29300129
            },
            "indexing": {
              "index_total": 46368,
              "index_time_in_millis": 78769,
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
              "query_total": 84,
              "query_time_in_millis": 209,
              "query_current": 0,
              "fetch_total": 2,
              "fetch_time_in_millis": 1,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2458,
              "total_time_in_millis": 537479,
              "total_docs": 9843016,
              "total_size_in_bytes": 7217295434,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 23106,
              "total_time_in_millis": 376567,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 28
            },
            "warmer": {
              "current": 0,
              "total": 23103,
              "total_time_in_millis": 1472
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 347,
              "hit_count": 103,
              "miss_count": 244,
              "cache_size": 0,
              "cache_count": 3,
              "evictions": 3
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 3,
              "memory_in_bytes": 47671,
              "terms_memory_in_bytes": 30964,
              "stored_fields_memory_in_bytes": 3728,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 12447,
              "doc_values_memory_in_bytes": 532,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 46368,
              "size_in_bytes": 62383671,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22597390
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 1,
              "miss_count": 39
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "kwpP6XYOqn2s1BVRUB62/A==",
              "generation": 4,
              "user_data": {
                "local_checkpoint": "46367",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "aypYjXSCQJ6CzwFRckQ3zg",
                "history_uuid": "RbOTDlpZQpCYB2zJaKnfeQ",
                "sync_id": "CqUicf_jR8GMhVpp7rgEgw",
                "translog_generation": "3",
                "max_seq_no": "46367"
              },
              "num_docs": 46368
            },
            "seq_no": {
              "max_seq_no": 46367,
              "local_checkpoint": 46367,
              "global_checkpoint": 46367
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 46368,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 29438692
            },
            "indexing": {
              "index_total": 46368,
              "index_time_in_millis": 72643,
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
              "query_total": 83,
              "query_time_in_millis": 387,
              "query_current": 0,
              "fetch_total": 2,
              "fetch_time_in_millis": 2,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2448,
              "total_time_in_millis": 564939,
              "total_docs": 9873886,
              "total_size_in_bytes": 7234994717,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 23083,
              "total_time_in_millis": 375355,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 28
            },
            "warmer": {
              "current": 0,
              "total": 23080,
              "total_time_in_millis": 1244
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 336,
              "hit_count": 94,
              "miss_count": 242,
              "cache_size": 0,
              "cache_count": 3,
              "evictions": 3
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 9,
              "memory_in_bytes": 76198,
              "terms_memory_in_bytes": 55188,
              "stored_fields_memory_in_bytes": 5712,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 13022,
              "doc_values_memory_in_bytes": 2276,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": -1,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 46368,
              "size_in_bytes": 62383671,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 22597400
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 2,
              "miss_count": 50
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGZlcw==",
              "generation": 5,
              "user_data": {
                "local_checkpoint": "46367",
                "max_unsafe_auto_id_timestamp": "-1",
                "translog_uuid": "GYnrz-HrT1adwtPiGQdz3w",
                "history_uuid": "RbOTDlpZQpCYB2zJaKnfeQ",
                "sync_id": "CqUicf_jR8GMhVpp7rgEgw",
                "translog_generation": "3",
                "max_seq_no": "46367"
              },
              "num_docs": 46368
            },
            "seq_no": {
              "max_seq_no": 46367,
              "local_checkpoint": 46367,
              "global_checkpoint": 46367
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    },
    ".monitoring-beats-6-2018.11.20": {
      "uuid": "rEFspiGgTcuMbvqY6FSTPg",
      "primaries": {
        "docs": {
          "count": 60480,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 37544063
        },
        "indexing": {
          "index_total": 60480,
          "index_time_in_millis": 97477,
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
          "query_total": 212,
          "query_time_in_millis": 1373,
          "query_current": 0,
          "fetch_total": 14,
          "fetch_time_in_millis": 15,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 2731,
          "total_time_in_millis": 669991,
          "total_docs": 12171417,
          "total_size_in_bytes": 8793450057,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 20971520
        },
        "refresh": {
          "total": 25452,
          "total_time_in_millis": 443082,
          "listeners": 0
        },
        "flush": {
          "total": 1,
          "periodic": 0,
          "total_time_in_millis": 25
        },
        "warmer": {
          "current": 0,
          "total": 25449,
          "total_time_in_millis": 1302
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 541,
          "hit_count": 98,
          "miss_count": 443,
          "cache_size": 0,
          "cache_count": 17,
          "evictions": 17
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 10,
          "memory_in_bytes": 94633,
          "terms_memory_in_bytes": 61587,
          "stored_fields_memory_in_bytes": 6872,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 16174,
          "doc_values_memory_in_bytes": 10000,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542672002517,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 55,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 55,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 47,
          "miss_count": 89
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "total": {
        "docs": {
          "count": 120960,
          "deleted": 0
        },
        "store": {
          "size_in_bytes": 74995919
        },
        "indexing": {
          "index_total": 120960,
          "index_time_in_millis": 192701,
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
          "query_total": 422,
          "query_time_in_millis": 2567,
          "query_current": 0,
          "fetch_total": 28,
          "fetch_time_in_millis": 29,
          "fetch_current": 0,
          "scroll_total": 0,
          "scroll_time_in_millis": 0,
          "scroll_current": 0,
          "suggest_total": 0,
          "suggest_time_in_millis": 0,
          "suggest_current": 0
        },
        "merges": {
          "current": 0,
          "current_docs": 0,
          "current_size_in_bytes": 0,
          "total": 5442,
          "total_time_in_millis": 1338485,
          "total_docs": 24528155,
          "total_size_in_bytes": 17698914283,
          "total_stopped_time_in_millis": 0,
          "total_throttled_time_in_millis": 0,
          "total_auto_throttle_in_bytes": 41943040
        },
        "refresh": {
          "total": 50705,
          "total_time_in_millis": 874003,
          "listeners": 0
        },
        "flush": {
          "total": 2,
          "periodic": 0,
          "total_time_in_millis": 49
        },
        "warmer": {
          "current": 0,
          "total": 50699,
          "total_time_in_millis": 2663
        },
        "query_cache": {
          "memory_size_in_bytes": 0,
          "total_count": 1059,
          "hit_count": 193,
          "miss_count": 866,
          "cache_size": 0,
          "cache_count": 35,
          "evictions": 35
        },
        "fielddata": {
          "memory_size_in_bytes": 0,
          "evictions": 0
        },
        "completion": {
          "size_in_bytes": 0
        },
        "segments": {
          "count": 19,
          "memory_in_bytes": 184725,
          "terms_memory_in_bytes": 119741,
          "stored_fields_memory_in_bytes": 13600,
          "term_vectors_memory_in_bytes": 0,
          "norms_memory_in_bytes": 0,
          "points_memory_in_bytes": 32020,
          "doc_values_memory_in_bytes": 19364,
          "index_writer_memory_in_bytes": 0,
          "version_map_memory_in_bytes": 0,
          "fixed_bit_set_memory_in_bytes": 0,
          "max_unsafe_auto_id_timestamp": 1542672002517,
          "file_sizes": {

          }
        },
        "translog": {
          "operations": 0,
          "size_in_bytes": 110,
          "uncommitted_operations": 0,
          "uncommitted_size_in_bytes": 110,
          "earliest_last_modified_age": 0
        },
        "request_cache": {
          "memory_size_in_bytes": 0,
          "evictions": 0,
          "hit_count": 89,
          "miss_count": 178
        },
        "recovery": {
          "current_as_source": 0,
          "current_as_target": 0,
          "throttle_time_in_millis": 0
        }
      },
      "shards": {
        "0": [
          {
            "routing": {
              "state": "STARTED",
              "primary": true,
              "node": "wfm-CgU_TI6clKOgKqJG-Q",
              "relocating_node": null
            },
            "docs": {
              "count": 60480,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 37544063
            },
            "indexing": {
              "index_total": 60480,
              "index_time_in_millis": 97477,
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
              "query_total": 212,
              "query_time_in_millis": 1373,
              "query_current": 0,
              "fetch_total": 14,
              "fetch_time_in_millis": 15,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2731,
              "total_time_in_millis": 669991,
              "total_docs": 12171417,
              "total_size_in_bytes": 8793450057,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 25452,
              "total_time_in_millis": 443082,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 25
            },
            "warmer": {
              "current": 0,
              "total": 25449,
              "total_time_in_millis": 1302
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 541,
              "hit_count": 98,
              "miss_count": 443,
              "cache_size": 0,
              "cache_count": 17,
              "evictions": 17
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 10,
              "memory_in_bytes": 94633,
              "terms_memory_in_bytes": 61587,
              "stored_fields_memory_in_bytes": 6872,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 16174,
              "doc_values_memory_in_bytes": 10000,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002517,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108691485
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 47,
              "miss_count": 89
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "RKHQqKWgEyAB6rl4AryLyg==",
              "generation": 4,
              "user_data": {
                "local_checkpoint": "60479",
                "max_unsafe_auto_id_timestamp": "1542672002517",
                "translog_uuid": "vtL1s-tyTBmnJ8nEHKN0xA",
                "history_uuid": "JZlEcfjeQC2IM0WdweS8xQ",
                "sync_id": "ugPkJqrPSS61wLXKxguWFA",
                "translog_generation": "4",
                "max_seq_no": "60479"
              },
              "num_docs": 60480
            },
            "seq_no": {
              "max_seq_no": 60479,
              "local_checkpoint": 60479,
              "global_checkpoint": 60479
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          },
          {
            "routing": {
              "state": "STARTED",
              "primary": false,
              "node": "aQxX2aAOSYuU0mZFT6JsbA",
              "relocating_node": null
            },
            "docs": {
              "count": 60480,
              "deleted": 0
            },
            "store": {
              "size_in_bytes": 37451856
            },
            "indexing": {
              "index_total": 60480,
              "index_time_in_millis": 95224,
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
              "query_total": 210,
              "query_time_in_millis": 1194,
              "query_current": 0,
              "fetch_total": 14,
              "fetch_time_in_millis": 14,
              "fetch_current": 0,
              "scroll_total": 0,
              "scroll_time_in_millis": 0,
              "scroll_current": 0,
              "suggest_total": 0,
              "suggest_time_in_millis": 0,
              "suggest_current": 0
            },
            "merges": {
              "current": 0,
              "current_docs": 0,
              "current_size_in_bytes": 0,
              "total": 2711,
              "total_time_in_millis": 668494,
              "total_docs": 12356738,
              "total_size_in_bytes": 8905464226,
              "total_stopped_time_in_millis": 0,
              "total_throttled_time_in_millis": 0,
              "total_auto_throttle_in_bytes": 20971520
            },
            "refresh": {
              "total": 25253,
              "total_time_in_millis": 430921,
              "listeners": 0
            },
            "flush": {
              "total": 1,
              "periodic": 0,
              "total_time_in_millis": 24
            },
            "warmer": {
              "current": 0,
              "total": 25250,
              "total_time_in_millis": 1361
            },
            "query_cache": {
              "memory_size_in_bytes": 0,
              "total_count": 518,
              "hit_count": 95,
              "miss_count": 423,
              "cache_size": 0,
              "cache_count": 18,
              "evictions": 18
            },
            "fielddata": {
              "memory_size_in_bytes": 0,
              "evictions": 0
            },
            "completion": {
              "size_in_bytes": 0
            },
            "segments": {
              "count": 9,
              "memory_in_bytes": 90092,
              "terms_memory_in_bytes": 58154,
              "stored_fields_memory_in_bytes": 6728,
              "term_vectors_memory_in_bytes": 0,
              "norms_memory_in_bytes": 0,
              "points_memory_in_bytes": 15846,
              "doc_values_memory_in_bytes": 9364,
              "index_writer_memory_in_bytes": 0,
              "version_map_memory_in_bytes": 0,
              "fixed_bit_set_memory_in_bytes": 0,
              "max_unsafe_auto_id_timestamp": 1542672002517,
              "file_sizes": {

              }
            },
            "translog": {
              "operations": 0,
              "size_in_bytes": 55,
              "uncommitted_operations": 0,
              "uncommitted_size_in_bytes": 55,
              "earliest_last_modified_age": 108691503
            },
            "request_cache": {
              "memory_size_in_bytes": 0,
              "evictions": 0,
              "hit_count": 42,
              "miss_count": 89
            },
            "recovery": {
              "current_as_source": 0,
              "current_as_target": 0,
              "throttle_time_in_millis": 0
            },
            "commit": {
              "id": "BJAtLLCV19Sh+00oWGK9fg==",
              "generation": 5,
              "user_data": {
                "local_checkpoint": "60479",
                "max_unsafe_auto_id_timestamp": "1542672002517",
                "translog_uuid": "itrAutvdREyzSOeIakbqdg",
                "history_uuid": "JZlEcfjeQC2IM0WdweS8xQ",
                "sync_id": "ugPkJqrPSS61wLXKxguWFA",
                "translog_generation": "4",
                "max_seq_no": "60479"
              },
              "num_docs": 60480
            },
            "seq_no": {
              "max_seq_no": 60479,
              "local_checkpoint": 60479,
              "global_checkpoint": 60479
            },
            "shard_path": {
              "state_path": "/usr/share/elasticsearch/data/nodes/0",
              "data_path": "/usr/share/elasticsearch/data/nodes/0",
              "is_custom_data_path": false
            }
          }
        ]
      }
    }
  }
}
""")

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
            # return MOCK_SHARDS_INFO
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
