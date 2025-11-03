ActiveAdmin.register Grid do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :grid, :l_name, :f_name, :dob, :sex, :race_preomb, :index_study, :mod_date, :mod_person, :ent_date, :ent_person, :note, :ss_num, :mrec_num, :research_status, :race, :ethnicity
  #
  # or
  #
  # permit_params do
  #   permitted = [:grid, :l_name, :f_name, :dob, :sex, :race_preomb, :index_study, :mod_date, :mod_person, :ent_date, :ent_person, :note, :ss_num, :mrec_num, :research_status, :race, :ethnicity]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  
index do
  id_column
  # column :grid
  column :l_name
  column :f_name
  column :index_study
  column :ent_date
  column :ent_person
  column :research_status
  actions
end
end
