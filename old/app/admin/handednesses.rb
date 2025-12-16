ActiveAdmin.register Handedness do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :a, :other_hand_a, :b, :other_hand_b, :c, :other_hand_c, :d, :other_hand_d, :e, :other_hand_e, :f, :other_hand_f, :g, :other_hand_g, :h, :other_hand_h, :i, :other_hand_i, :j, :other_hand_j, :foot, :eye, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :a, :other_hand_a, :b, :other_hand_b, :c, :other_hand_c, :d, :other_hand_d, :e, :other_hand_e, :f, :other_hand_f, :g, :other_hand_g, :h, :other_hand_h, :i, :other_hand_i, :j, :other_hand_j, :foot, :eye, :administrator, :verified_by]
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
  #filter :id
  #filter :subject
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
      f.input :a
      f.input :other_hand_a
      f.input :b
      f.input :other_hand_b
      f.input :c
      f.input :other_hand_c
      f.input :d
      f.input :other_hand_d
      f.input :e
      f.input :other_hand_e
      f.input :f
      f.input :other_hand_f
      f.input :g
      f.input :other_hand_g
      f.input :h
      f.input :other_hand_h
      f.input :i
      f.input :other_hand_i
      f.input :j
      f.input :other_hand_j
      f.input :foot
      f.input :eye
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons 
    end
end
