ActiveAdmin.register Bicro do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :injury_type, :q1, :q2, :q3, :q4, :q5, :q6, :q7, :q8, :q9, :q10, :q11, :q12, :q13, :q14, :q15, :q16, :q17, :q18, :q19, :q20, :q21, :q22, :q23, :q24, :q25, :q26, :q27, :q28, :q29, :q30, :q31, :q32, :q33, :q34, :q35, :q36, :q37, :q38, :q39, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :injury_type, :q1, :q2, :q3, :q4, :q5, :q6, :q7, :q8, :q9, :q10, :q11, :q12, :q13, :q14, :q15, :q16, :q17, :q18, :q19, :q20, :q21, :q22, :q23, :q24, :q25, :q26, :q27, :q28, :q29, :q30, :q31, :q32, :q33, :q34, :q35, :q36, :q37, :q38, :q39, :administrator, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  index do
    id_column
    column :subject_id
    column :date
    column :visit_num
    column :study_id
    column :injury_type
    column :administrator
    column :verified_by
    actions
  end 

  # specify filters
  #filter :id
  #filter :subject_id
  #filter :date
  #filter :visit_num
  #filter :administrator
  #filter :verified_by

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
      f.input :injury_type
      f.input :q1
      f.input :q2
      f.input :q3
      f.input :q4
      f.input :q5
      f.input :q6
      f.input :q7
      f.input :q8
      f.input :q9
      f.input :q10
      f.input :q11
      f.input :q12
      f.input :q13
      f.input :q14
      f.input :q15
      f.input :q16
      f.input :q17
      f.input :q18
      f.input :q19
      f.input :q20
      f.input :q21
      f.input :q22
      f.input :q23
      f.input :q24
      f.input :q25
      f.input :q26
      f.input :q27
      f.input :q28
      f.input :q29
      f.input :q30
      f.input :q31
      f.input :q32
      f.input :q33
      f.input :q34
      f.input :q35
      f.input :q36
      f.input :q37
      f.input :q38
      f.input :q39
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons 
    end
end
