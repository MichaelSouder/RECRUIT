class Bis11 < ApplicationRecord
  self.table_name = 'bis_raw'

  belongs_to :subject
end
