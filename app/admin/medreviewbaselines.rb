ActiveAdmin.register Medreviewbaseline do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :q1, :q2_med_01, :q2_med_01_dose, :q2_med_01_start, :q2_med_02, :q2_med_02_dose, :q2_med_02_start, :q2_med_03, :q2_med_03_dose, :q2_med_03_start, :q2_med_04, :q2_med_04_dose, :q2_med_04_start, :q2_med_05, :q2_med_05_dose, :q2_med_05_start, :q2_med_06, :q2_med_06_dose, :q2_med_06_start, :q2_med_07, :q2_med_07_dose, :q2_med_07_start, :q2_med_08, :q2_med_08_dose, :q2_med_08_start, :q2_med_09, :q2_med_09_dose, :q2_med_09_start, :q2_med_10, :q2_med_10_dose, :q2_med_10_start, :q2_med_11, :q2_med_11_dose, :q2_med_11_start, :q2_med_12, :q2_med_12_dose, :q2_med_12_start, :q2_med_13, :q2_med_13_dose, :q2_med_13_start, :q2_med_14, :q2_med_14_dose, :q2_med_14_start, :q2_med_15, :q2_med_15_dose, :q2_med_15_start, :q2_med_other, :q3, :q3_comments, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :q1, :q2_med_01, :q2_med_01_dose, :q2_med_01_start, :q2_med_02, :q2_med_02_dose, :q2_med_02_start, :q2_med_03, :q2_med_03_dose, :q2_med_03_start, :q2_med_04, :q2_med_04_dose, :q2_med_04_start, :q2_med_05, :q2_med_05_dose, :q2_med_05_start, :q2_med_06, :q2_med_06_dose, :q2_med_06_start, :q2_med_07, :q2_med_07_dose, :q2_med_07_start, :q2_med_08, :q2_med_08_dose, :q2_med_08_start, :q2_med_09, :q2_med_09_dose, :q2_med_09_start, :q2_med_10, :q2_med_10_dose, :q2_med_10_start, :q2_med_11, :q2_med_11_dose, :q2_med_11_start, :q2_med_12, :q2_med_12_dose, :q2_med_12_start, :q2_med_13, :q2_med_13_dose, :q2_med_13_start, :q2_med_14, :q2_med_14_dose, :q2_med_14_start, :q2_med_15, :q2_med_15_dose, :q2_med_15_start, :q2_med_other, :q3, :q3_comments, :administrator, :verified_by]
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
      f.input :q2_med_01
      f.input :q2_med_01_dose
      f.input :q2_med_01_start, :label => "Med 01 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_02
      f.input :q2_med_02_dose
      f.input :q2_med_02_start, :label => "Med 02 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_03
      f.input :q2_med_03_dose
      f.input :q2_med_03_start, :label => "Med 03 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_04
      f.input :q2_med_04_dose
      f.input :q2_med_04_start, :label => "Med 04 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_05
      f.input :q2_med_05_dose
      f.input :q2_med_05_start, :label => "Med 05 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_06
      f.input :q2_med_06_dose
      f.input :q2_med_06_start, :label => "Med 06 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_07
      f.input :q2_med_07_dose
      f.input :q2_med_07_start, :label => "Med 07 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_08
      f.input :q2_med_08_dose
      f.input :q2_med_08_start, :label => "Med 08 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_09
      f.input :q2_med_09_dose
      f.input :q2_med_09_start, :label => "Med 09 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_10
      f.input :q2_med_10_dose
      f.input :q2_med_10_start, :label => "Med 10 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_11
      f.input :q2_med_11_dose
      f.input :q2_med_11_start, :label => "Med 11 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_12
      f.input :q2_med_12_dose
      f.input :q2_med_12_start, :label => "Med 12 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_13
      f.input :q2_med_13_dose
      f.input :q2_med_13_start, :label => "Med 13 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_14
      f.input :q2_med_14_dose
      f.input :q2_med_14_start, :label => "Med 14 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_15
      f.input :q2_med_15_dose
      f.input :q2_med_15_start, :label => "Med 15 date start (yyyy-mm-dd)", as: :datepicker
      f.input :q2_med_other
      f.input :q3
      f.input :q3_comments
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons 
    end
end
