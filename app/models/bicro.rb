class Bicro < ApplicationRecord
    self.table_name = 'bicro_raw'

    belongs_to :subject
end
