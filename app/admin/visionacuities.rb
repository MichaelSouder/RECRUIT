ActiveAdmin.register Visionacuity do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :visit_num, :date, :study_id, :sex, :date_of_birth, :q1, :q1a, :q2, :q3, :q4_spectralis, :q4_spectralis_comments, :q5_cirrus, :q5_cirrus_comments, :q6_lsfg, :q6_lsfg_comments, :q7_acuity, :q7_acuity_comments, :q8_contrast, :q8_contrast_comments, :q9_vf, :q9_vf_comments, :q10_pupil, :q10_pupil_comments, :q11_hitt, :q11_hitt_comments, :comments, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :visit_num, :date, :study_id, :sex, :date_of_birth, :q1, :q1a, :q2, :q3, :q4_spectralis, :q4_spectralis_comments, :q5_cirrus, :q5_cirrus_comments, :q6_lsfg, :q6_lsfg_comments, :q7_acuity, :q7_acuity_comments, :q8_contrast, :q8_contrast_comments, :q9_vf, :q9_vf_comments, :q10_pupil, :q10_pupil_comments, :q11_hitt, :q11_hitt_comments, :comments, :administrator, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  form do |f|
    f.semantic_errors
    f.inputs  do    
      f.input :subject, :label => "Subject ID"
      f.input :visit_num
      f.input :date, as: :datepicker, 
      datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
      }
      f.input :study_id
      f.input :sex
      f.input :date_of_birth, as: :datepicker, 
      datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
      }
      f.input :q1
      f.input :q1a
      f.input :q2
      f.input :q3
      f.input :q4_spectralis
      f.input :q4_spectralis_comments
      f.input :q5_cirrus
      f.input :q5_cirrus_comments
      f.input :q6_lsfg
      f.input :q6_lsfg_comments
      f.input :q7_acuity
      f.input :q7_acuity_comments
      f.input :q8_contrast
      f.input :q8_contrast_comments
      f.input :q9_vf
      f.input :q9_vf_comments
      f.input :q10_pupil
      f.input :q10_pupil_comments
      f.input :q11_hitt
      f.input :q11_hitt_comments
      f.input :comments
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons
  end

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
# filter :subject
# filter :date
# filter :study_id
# filter :visit_num
# filter :administrator
# filter :verified_by
end
