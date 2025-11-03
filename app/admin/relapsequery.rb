ActiveAdmin.register Relapsequery do

require 'date'
  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
permit_params :subject_id, :date, :study_id, :visit_num, :q1, :explanation, :administrator, :verified_by, :time_stamp
  
index do
  id_column
  column :subject_id
  column :date
  column :visit_num
  column :study_id
  column :q1
  column :explanation
  column :administrator
  column :verified_by
  actions 
end

form do |f|
  f.semantic_errors
  f.inputs  do    
    f.input :date, :label => "Today's Date (yyyy-mm-dd)", as: :datepicker,
    datepicker_options: {
      min_date: "1900-01-01",
      max_date: "+3D"
    } 
    f.input :subject_id, :label => "Subject ID"
    f.input :visit_num, :label => "Visit Number"
    f.input :study_id
    f.input :q1
    f.input :explanation
    f.input :administrator
    f.input :verified_by
  end
  f.actions         
end
end
