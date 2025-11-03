ActiveAdmin.register Contrastsensitivity do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :study_id, :"#_correct_A", :contrast_score_a, :"#_correct_B", :contrast_score_b, :"#_correct_C", :contrast_score_c, :"#_correct_D", :contrast_score_d, :"#_correct_E", :contrast_score_e, :eye_recorded, :luminance, :glare, :correction, :examiner, :test_comments, :raw_data, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :study_id, :"#_correct_A", :contrast_score_a, :"#_correct_B", :contrast_score_b, :"#_correct_C", :contrast_score_c, :"#_correct_D", :contrast_score_d, :"#_correct_E", :contrast_score_e, :eye_recorded, :luminance, :glare, :correction, :examiner, :test_comments, :raw_data, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  
  index do
    id_column
    column :subject
    column :date
    column :study_id
    column :examiner
    column :verified_by
    actions
  end 

  # specify filters
  #filter :id
  #filter :subject
  #filter :date
  #filter :examiner
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
      f.input :study_id, :label => "Study ID"
      f.input :'#_correct_A'
      f.input :contrast_score_a
      f.input :'#_correct_B'
      f.input :contrast_score_b
      f.input :'#_correct_C'
      f.input :contrast_score_c
      f.input :'#_correct_D'
      f.input :contrast_score_d
      f.input :'#_correct_E'
      f.input :contrast_score_e
      f.input :eye_recorded
      f.input :luminance
      f.input :glare
      f.input :correction
      f.input :examiner
      f.input :test_comments
      f.input :raw_data
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons 
    end
end
