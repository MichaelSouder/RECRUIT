class Bisbas < ApplicationRecord
    self.table_name = 'bis_bas_raw'

    belongs_to :subject
end
