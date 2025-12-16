class Sessionnote < ApplicationRecord
    self.table_name = 'session_notes'

    belongs_to :subject
end
