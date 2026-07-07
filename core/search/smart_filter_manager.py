from core.search.smart_filter import built_in_smart_filters


class SmartFilterManager:
    def __init__(self, database, filters=None):
        self.database = database
        self.filters = filters or built_in_smart_filters()
        self.filters_by_id = {
            smart_filter.id: smart_filter
            for smart_filter in self.filters
        }

    def list_filters(self):
        return list(self.filters)

    def get_filter(self, filter_id):
        return self.filters_by_id.get(filter_id)

    def matching_records(self, project_path, filter_id):
        smart_filter = self.get_filter(filter_id)

        if smart_filter is None:
            return []

        return [
            record
            for record in self.database.export_records(project_path)
            if smart_filter.matches(record)
        ]

    def matching_file_paths(self, project_path, filter_id):
        return [
            record.file_path
            for record in self.matching_records(project_path, filter_id)
        ]
