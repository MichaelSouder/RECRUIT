ActiveAdmin.register Medreviewfollowup do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :q1, :q1_medchange_01, :q1_medchange_01_dose, :q1_medchange_01_date, :q1_medchange_02, :q1_medchange_02_dose, :q1_medchange_02_date, :q1_medchange_03, :q1_medchange_03_dose, :q1_medchange_03_date, :q1_medchange_04, :q1_medchange_04_dose, :q1_medchange_04_date, :q1_medchange_05, :q1_medchange_05_dose, :q1_medchange_05_date, :q1_medchange_other, :q2, :q2_comments, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :q1, :q1_medchange_01, :q1_medchange_01_dose, :q1_medchange_01_date, :q1_medchange_02, :q1_medchange_02_dose, :q1_medchange_02_date, :q1_medchange_03, :q1_medchange_03_dose, :q1_medchange_03_date, :q1_medchange_04, :q1_medchange_04_dose, :q1_medchange_04_date, :q1_medchange_05, :q1_medchange_05_dose, :q1_medchange_05_date, :q1_medchange_other, :q2, :q2_comments, :administrator, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  
  index do
    id_column
    column :subject
    column :date
    column :visit_num
    column :study_id
    column :administrator
    column :verified_by
    actions
  end 

  # specify filters
  # filter :id
  # filter :subject
  # filter :date
  # filter :visit_num
  # filter :administrator
  # filter :verified_by
  
  form do |f|
    f.semantic_errors
    f.inputs  do    
      f.input :subject, :label => "Subject ID"
      f.input :date, :label => "Date (yyyy-mm-dd)", as: :datepicker,
      datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
      }
      f.input :visit_num
      f.input :study_id, :label => "Study ID"
      f.input :q1
      f.input :q1_medchange_01
      f.input :q1_medchange_01_dose
      f.input :q1_medchange_01_date, :label => "medchange 01 date (yyyy-mm-dd)", as: :datepicker
      f.input :q1_medchange_02
      f.input :q1_medchange_02_dose
      f.input :q1_medchange_02_date, :label => "medchange 02 date (yyyy-mm-dd)", as: :datepicker
      f.input :q1_medchange_03
      f.input :q1_medchange_03_dose
      f.input :q1_medchange_03_date, :label => "medchange 03 date (yyyy-mm-dd)", as: :datepicker
      f.input :q1_medchange_04
      f.input :q1_medchange_04_dose
      f.input :q1_medchange_04_date, :label => "medchange 04 date (yyyy-mm-dd)", as: :datepicker
      f.input :q1_medchange_05
      f.input :q1_medchange_05_dose
      f.input :q1_medchange_05_date, :label => "medchange 05 date (yyyy-mm-dd)", as: :datepicker
      f.input :q1_medchange_other
      f.input :q2
      f.input :q2_comments
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons 
    end
end
