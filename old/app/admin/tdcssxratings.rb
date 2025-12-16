ActiveAdmin.register Tdcssxrating do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :event_id, :date, :time, :study_id, :pre_post, :visit_num, :page_link, :headache_severity, :neck_pain_severity, :scalp_pain_severity, :tingling_severity, :itching_severity, :burning_severity, :skin_redness_severity, :sleepiness_severity, :concentration_severity, :mood_change_severity, :nauseau_severity, :other_symptom, :other_severity, :administrator, :time_stamp, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :event_id, :date, :time, :study_id, :pre_post, :visit_num, :page_link, :headache_severity, :neck_pain_severity, :scalp_pain_severity, :tingling_severity, :itching_severity, :burning_severity, :skin_redness_severity, :sleepiness_severity, :concentration_severity, :mood_change_severity, :nauseau_severity, :other_symptom, :other_severity, :administrator, :time_stamp, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  form do |f|
    f.semantic_errors
    f.inputs  do
      f.input :subject, :label => "Subject ID"
      f.input :date, :label => "Date (yyyy-mm-dd)",
                as: :datepicker,
                      datepicker_options: {
                        min_date: "1900-01-01",
                        max_date: "+3D"
                      }
      f.input :time, :label => "Time (HH:MM:SS)"
      f.input :study_id
      f.input :pre_post
      f.input :visit_num
      f.input :headache_severity
      f.input :neck_pain_severity
      f.input :scalp_pain_severity
      f.input :tingling_severity
      f.input :itching_severity
      f.input :burning_severity
      f.input :skin_redness_severity
      f.input :sleepiness_severity
      f.input :concentration_severity
      f.input :mood_change_severity
      f.input :nauseau_severity
      f.input :other_symptom
      f.input :time_stamp, as: :datetime_picker
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
  # filter :id
  # filter :subject
  # filter :date
  # filter :study_id
  # filter :pre_post
  # filter :visit_num
  # filter :administrator
  # filter :verified_by
  
end

