"""AlgoliaHelper
Wrapper on top of the AlgoliaSearch API client"""

from algoliasearch import algoliasearch
from builtins import range

class AlgoliaHelper:
    """AlgoliaHelper"""
    def __init__(self, app_id, api_key, index_name, settings, query_rules, repo):
        self.algolia_client = algoliasearch.Client(app_id, api_key)
        self.index_name = index_name
        self.index_name_tmp = index_name + '_tmp'
        self.algolia_index = self.algolia_client.init_index(self.index_name)
        taskID = self.algolia_client.copy_index(self.index_name, self.index_name_tmp)['taskID']
        self.algolia_index.wait_task(taskID)
        self.algolia_index_tmp = self.algolia_client.init_index(self.index_name_tmp)
        # self.algolia_client.delete_index(self.index_name_tmp)
        self.algolia_index_tmp.set_settings(settings)

        # purge old records of this repo
        self.algolia_index_tmp.delete_by_query('', {'facetFilters': 'repo:{}'.format(repo)})

        if len(query_rules) > 0:
            # self.algolia_index_tmp.batch_rules(query_rules, True, True)
            self.algolia_index.batch_rules(query_rules, True, True)

    def add_records(self, records, url, from_sitemap):
        """Add new records to the temporary index"""
        record_count = len(records)
        for i in range(0, record_count, 50):
            self.algolia_index_tmp.add_objects(records[i:i + 50])

        color="96" if from_sitemap else "94"

        print("\033["+color+"m> DocSearch: \033[0m" + url + " (\033[93m" + str(record_count) + " records\033[0m)")

    def add_synonyms(self, synonyms):
        synonyms_list = []
        for key, value in synonyms.iteritems():
            synonyms_list.append(value)

        # self.algolia_index_tmp.batch_synonyms(synonyms_list)
        self.algolia_index.batch_synonyms(synonyms_list)
        print("\033[94m> DocSearch: \033[0m" + "Synonyms" + " (\033[93m" + str(len(synonyms_list)) + " synonyms\033[0m)")

    def commit_tmp_index(self):
        """Overwrite the real index with the temporary one"""
        # print("Update settings")
        self.algolia_client.move_index(self.index_name_tmp, self.index_name)

    def report_crawling_issue(self):
        self.algolia_index.set_settings({
            'userData': {
                'crawling_issue': True
            }
        })
