class Verbalfluency < ApplicationRecord
    self.table_name = 'verbal_fluency'
    
    belongs_to :subject
end
