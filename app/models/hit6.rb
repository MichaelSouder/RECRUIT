class Hit6 < ApplicationRecord
  self.table_name = 'hit6_raw'

  belongs_to :subject
end
