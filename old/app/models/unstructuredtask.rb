class Unstructuredtask < ApplicationRecord
    self.table_name = 'unstructured_task'

    belongs_to :subject
end
