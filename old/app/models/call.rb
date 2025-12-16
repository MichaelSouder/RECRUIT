class Call < ApplicationRecord
  self.table_name = 'call_log'

  belongs_to :subject
end
