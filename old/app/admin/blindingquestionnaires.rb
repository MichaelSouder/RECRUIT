ActiveAdmin.register Blindingquestionnaire do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :' visit_num', :date, :study_id, :q1, :q2, :q3, :stimulation, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :" visit_num", :date, :study_id, :q1, :q2, :q3, :stimulation, :administrator, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  index do
    id_column
    column :subject
    column :" visit_num"
    column :date
    column :study_id
    column :administrator
    column :verified_by
    actions
  end 

  form do |f|
    f.semantic_errors
    f.inputs  do    
      f.input :subject, :label => "Subject ID"
      f.input :' visit_num'
      f.input :date, :label => "Date (yyyy-mm-dd)", as: :datepicker,
      datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
      }
      f.input :study_id, :label => "Study ID"
      f.input :q1
      f.input :q2
      f.input :q3
      f.input :stimulation
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons 
    end
end

