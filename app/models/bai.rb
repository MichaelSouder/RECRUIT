class Bai < ApplicationRecord
    self.table_name = 'bai'

    belongs_to :subject
end