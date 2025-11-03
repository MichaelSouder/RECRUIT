class Visionacuity < ApplicationRecord
    self.table_name = 'vision_assessments'

    belongs_to :subject
end