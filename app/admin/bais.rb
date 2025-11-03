ActiveAdmin.register Bai do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :q1, :q2, :q3, :q4, :q5, :q6, :q7, :q8, :q9, :q10, :q11, :q12, :q13, :q14, :q15, :q16, :q17, :q18, :q19, :q20, :q21, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :q1, :q2, :q3, :q4, :q5, :q6, :q7, :q8, :q9, :q10, :q11, :q12, :q13, :q14, :q15, :q16, :q17, :q18, :q19, :q20, :q21, :administrator, :verified_by]
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
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons 
    end
end
