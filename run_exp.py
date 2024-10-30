from alns import Alns
from base import QuestionDataHandle
def run(data_file,seed):
    (deposite_list, cargo_site_dict,metro_cargo_site_dict, normal_cargo_site_dict,points_df, distance_matrix_df, time_matrix_df,
     metro_travel_times, metro_schedule_df, departure_times_df, riv_ijk_indices_df) = QuestionDataHandle().get_data(
        data_file)
    Alns(deposite_list, cargo_site_dict,metro_cargo_site_dict,normal_cargo_site_dict,departure_times_df)()

def main(data_file,seed):
    run(data_file,seed)

if __name__ == '__main__':
    seed = 45
    data_file = rf'E:\mathorcup\bike sharing\ALNS_BIKE\data\seed_{seed}\data_seed_{seed}.pkl'
    main(data_file,seed)