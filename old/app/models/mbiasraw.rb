class Mbiasraw < ApplicationRecord
    self.table_name = 'mbias_raw'

    belongs_to :subject
end
