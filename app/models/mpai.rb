class Mpai < ApplicationRecord
  self.table_name = 'mpai_raw'

  belongs_to :subject

end
