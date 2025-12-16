class Demographic < ApplicationRecord
    self.table_name = 'demographics'

    belongs_to :subject
end
