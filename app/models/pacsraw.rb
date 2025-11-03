class Pacsraw < ApplicationRecord
    self.table_name = 'pacs_raw'
  
    belongs_to :subject
  end
  