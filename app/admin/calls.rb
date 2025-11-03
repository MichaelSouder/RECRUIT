ActiveAdmin.register Call do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :date_of_call, :subject_id, :study, :first_name, :last_name, :phone_num, :last4_ssn, :date_of_birth, :subject_id, :study, :referral_source, :tbi, :initial_call_back, :initial_screen, :second_call_back, :third_call_back, :status, :other_studies, :not_interested, :reason_not_interested, :comments, :managed_by, :entered_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:date_of_call, :first_name, :last_name, :phone_num, :last4_ssn, :date_of_birth, :subject_id, :study, :referral_source, :tbi, :initial_call_back, :initial_screen, :second_call_back, :third_call_back, :status, :other_studies, :not_interested, :reason_not_interested, :comments, :managed_by, :entered_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end

  index do
    id_column
    column :date_of_call
    column :subject
    column :first_name
    column :last_name
    column :last4_ssn
    column :study
    column :referral_source
    column :status
    column :comments
    actions
  end 

  # specify filters
  filter :date_of_call
  filter :subject
  filter :first_name
  filter :last_name
  filter :last4_ssn
  filter :study_id
  filter :referral_source
  filter :status
  filter :comments

end
