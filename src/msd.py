import sys
import os
from spotify import SpotifyInterface

h5_lib_path = '/home/ubuntu/MSongsDB/PythonSrc'
sys.path.append(h5_lib_path)
import hdf5_getters as h5

class MSDInterface:
    '''
    Retrieves song data from the Million Song Dataset.
    '''

    def get_music(self):

        files_list = self.get_files()
        songs = [self.process_song(file) for file in files_list]
        songs = [s for s in songs if s is not None]
        #print(len(songs))

        self.clear_tmp()

        return songs

    def get_files(self):

        root_path = '/home/ubuntu/tmp'
        files_list = []

        for root, dirs, files in os.walk(root_path):
            files_subset = [os.path.join(root, f) for f in files if f.endswith('.h5')]
            files_list += files_subset

        return files_list

    def process_song(self, song_path):
        # read file
        song_data = h5.open_h5_file_read(song_path)

	# process file
        print(str(h5.get_song_id(song_data).decode('UTF-8')) + '   ' + str(h5.get_song_id(song_data)))
        song_id = h5.get_song_id(song_data).decode('UTF-8')
        song_int_id = int(h5.get_track_7digitalid(song_data))
        song_name = h5.get_title(song_data).decode('UTF-8').lower()
        artist_name = h5.get_artist_name(song_data).decode('UTF-8').lower()
        song_year = int(h5.get_year(song_data))

        sp = SpotifyInterface()
        track_info = sp.search_track_info(artist_name, song_name)

        if track_info == None:
            song_data.close()
            return None

        timbre = self.ndarray_list_to_ndlist(h5.get_segments_timbre(song_data))
        chroma = self.ndarray_list_to_ndlist(h5.get_segments_pitches(song_data))

        song_data.close()

        song_dict = {'id': song_int_id, 'source_id': song_id, 'name': song_name, 
                    'artist': artist_name, 'year': song_year, 'timbre': timbre, 
                    'chroma': chroma, **track_info}

        return song_dict

    def ndarray_list_to_ndlist(self, ndarry_list):

        ndlist = [ndarr.tolist() for ndarr in ndarry_list]

        return ndlist

    def clear_tmp(self):
        # delete all tmp files
        mydir = '/home/ubuntu/tmp'
        list(map(os.unlink, (os.path.join( mydir,f) for f in os.listdir(mydir))))

if (__name__ == '__main__'):

    msdi = MSDInterface()
    songs = msdi.get_music()
    print(len(songs))
    for s in songs:
        print(s['artist'],s['popularity'], s['url'])
