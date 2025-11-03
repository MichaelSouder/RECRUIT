class Auditc < ApplicationRecord
  self.table_name = 'audit_c'
  
  belongs_to :subject
end
