# -*- coding: utf-8 -*-
"""Local database access and functions"""
from __future__ import unicode_literals

import resources.lib.common as common
import resources.lib.database.db_base as db_base
import resources.lib.database.db_local as db_local
import resources.lib.database.db_utils as db_utils


class NFSharedDatabase(db_local.NFLocalDatabase):
    @db_base.sql_connect()
    def get_movie_filepath(self, videoid, default_value=None):
        """Get movie filepath for given videoid"""
        query = 'SELECT FilePath FROM VideoLibMovies WHERE VideoID = ?'
        cur = self._execute_query(query, (videoid,))
        result = cur.fetchone()
        return result[0] if result else default_value

    @db_base.sql_connect()
    def get_episode_filepath(self, tvshowid, seasonid, episodeid, default_value=None):
        """Get movie filepath for given videoid"""
        query =\
            ('SELECT FilePath FROM VideoLibEpisodes '
             'INNER JOIN VideoLibSeasons ON VideoLibEpisodes.SeasonID = VideoLibSeasons.SeasonID '
             'WHERE VideoLibSeasons.TvShowID = ? AND '
             'VideoLibSeasons.SeasonID = ? AND '
             'VideoLibEpisodes.EpisodeID = ?')
        cur = self._execute_query(query, (videoid, seasonid, episodeid))
        result = cur.fetchone()
        return result[0] if result else default_value

    @db_base.sql_connect()
    def get_random_episode_filepath_from_tvshow(self, tvshowid, default_value=None):
        """Get random episode filepath of a show of a given videoid"""
        query =\
            ('SELECT FilePath FROM VideoLibEpisodes '
             'INNER JOIN VideoLibSeasons ON VideoLibEpisodes.SeasonID = VideoLibSeasons.SeasonID '
             'WHERE VideoLibSeasons.TvShowID = ? '
             'ORDER BY RANDOM() LIMIT 1')
        cur = self._execute_query(query, (tvshowid,))
        result = cur.fetchone()
        return result[0] if result else default_value

    @db_base.sql_connect()
    def get_random_episode_filepath_from_season(self, tvshowid, seasonid, default_value=None):
        """Get random episode filepath of a show of a given videoid"""
        query =\
            ('SELECT FilePath FROM VideoLibEpisodes '
             'INNER JOIN VideoLibSeasons ON VideoLibEpisodes.SeasonID = VideoLibSeasons.SeasonID '
             'WHERE VideoLibSeasons.TvShowID = ? AND VideoLibSeasons.SeasonID = ? '
             'ORDER BY RANDOM() LIMIT 1')
        cur = self._execute_query(query, (tvshowid, seasonid))
        result = cur.fetchone()
        return result[0] if result else default_value

    @db_base.sql_connect()
    def get_all_video_id_list(self):
        """Get all the ids of movies and tvshows contained in the library"""
        self.conn.row_factory = lambda cursor, row: row[0]
        query = ('SELECT MovieID FROM VideoLibMovies '
                 'UNION '
                 'SELECT TvShowID FROM VideoLibTvShows')
        cur = self._execute_query(query)
        result = cur.fetchall()
        return result

    @db_base.sql_connect()
    def get_tvshows_id_list(self):
        """Get all the ids of tvshows contained in the library"""
        self.conn.row_factory = lambda cursor, row: row[0]
        query = 'SELECT TvShowID FROM VideoLibTvShows'
        cur = self._execute_query(query)
        result = cur.fetchall()
        return result

    @db_base.sql_connect()
    def get_movies_id_list(self):
        """Get all the ids of movies contained in the library"""
        self.conn.row_factory = lambda cursor, row: row[0]
        query = 'SELECT MovieID FROM VideoLibMovies'
        cur = self._execute_query(query)
        result = cur.fetchall()
        return result

    @db_base.sql_connect()
    def movie_id_exists(self, movieid):
        """Return True if a movie id exists"""
        query = 'SELECT EXISTS(SELECT 1 FROM VideoLibMovies WHERE MovieID = ?)'
        cur = self._execute_query(query, (movieid,))
        return bool(cur.fetchone())

    @db_base.sql_connect()
    def tvshow_id_exists(self, tvshowid):
        """Return True if a tvshow id exists"""
        query = 'SELECT EXISTS(SELECT 1 FROM VideoLibTvShows WHERE TvShowID = ?)'
        cur = self._execute_query(query, (tvshowid,))
        return bool(cur.fetchone())

    @db_base.sql_connect()
    def season_id_exists(self, tvshowid, seasonid):
        """Return True if a tvshow season id exists"""
        query =\
            ('SELECT EXISTS('
             'SELECT 1 FROM VideoLibSeasons '
             'INNER JOIN VideoLibTvShows ON VideoLibSeasons.TvShowID = VideoLibTvShows.TvShowID '
             'WHERE VideoLibTvShows.TvShowID = ? AND VideoLibSeasons.SeasonID = ?)')
        cur = self._execute_query(query, (tvshowid, seasonid))
        return bool(cur.fetchone())

    @db_base.sql_connect()
    def episode_id_exists(self, tvshowid, seasonid, episodeid):
        """Return True if a tvshow episode id exists"""
        query =\
            ('SELECT EXISTS('
             'SELECT 1 FROM VideoLibEpisodes'
             'INNER JOIN VideoLibSeasons ON VideoLibEpisodes.SeasonID = VideoLibSeasons.SeasonID '
             'INNER JOIN VideoLibTvShows ON VideoLibSeasons.TvShowID = VideoLibTvShows.TvShowID '
             'WHERE VideoLibTvShows.TvShowID = ? AND '
             'VideoLibSeasons.SeasonID = ? AND '
             'VideoLibEpisodes.EpisodeID = ?)')
        cur = self._execute_query(query, (tvshowid, seasonid, episodeid))
        return bool(cur.fetchone())

    @db_base.sql_connect()
    def set_tvshow_exclude_update(self, tvshowid, value):
        update_query = 'UPDATE VideoLibTvShows SET ExcludeUpdate = ? WHERE TvShowID = ?'
        value = common.convert_to_string(value)
        cur = self._execute_query(update_query, (tvshowid, value))

    @db_base.sql_connect()
    def get_tvshow_exclude_update(self, tvshowid):
        query = 'SELECT ExcludeUpdate FROM VideoLibTvShows WHERE TvShowID = ?'
        cur = self._execute_query(query, (tvshowid,))
        result = cur.fetchone()
        return common.convert_from_string(result[0], bool) if result else False

    @db_base.sql_connect()
    def set_movie(self, movieid, file_path, nfo_export):
        """Update or insert a movie"""
        # Update or insert approach, if there is no updated row then insert new one
        update_query = ('UPDATE VideoLibMovies SET FilePath = ?, NfoExport = ? '
                        'WHERE MovieID = ?')
        cur = self._execute_query(update_query, (file_path, nfo_export, movieid))
        if cur.rowcount == 0:
            insert_query =\
                'INSERT INTO VideoLibMovies (MovieID, FilePath, NfoExport) VALUES (?, ?, ?)'
            self._execute_non_query(insert_query, (movieid, file_path, nfo_export))

    @db_base.sql_connect()
    def set_tvshow(self, tvshowid, nfo_export, exclude_update):
        """Update or insert a tvshow"""
        # Update or insert approach, if there is no updated row then insert new one
        update_query = ('UPDATE VideoLibTvShows SET NfoExport = ?, ExcludeUpdate = ? '
                        'WHERE TvShowID = ?')
        cur = self._execute_query(update_query, (str(nfo_export), str(exclude_update), tvshowid))
        if cur.rowcount == 0:
            insert_query =\
                ('INSERT INTO VideoLibTvShows (TvShowID, NfoExport, ExcludeUpdate) '
                 'VALUES (?, ?, ?, ?)')
            self._execute_non_query(insert_query, (tvshowid, str(nfo_export), str(exclude_update)))

    @db_base.sql_connect()
    def insert_season(self, tvshowid, seasonid):
        """Insert a season if not exists"""
        if not self.season_id_exists(videoid, seasonid):
            insert_query = ('INSERT INTO VideoLibSeasons (TvShowID, SeasonID) '
                            'VALUES (?, ?)')
            self._execute_non_query(insert_query, (tvshowid, seasonid))

    @db_base.sql_connect()
    def insert_episode(self, tvshowid, seasonid, episodeid, file_path):
        """Insert a episode if not exists"""
        if not self.episode_id_exists(tvshowid, seasonid, episodeid):
            insert_query = ('INSERT INTO VideoLibEpisodes (SeasonID, EpisodeID, FilePath) '
                            'VALUES (?, ?, ?)')
            self._execute_non_query(insert_query, (seasonid, episodeid, file_path))

    @db_base.sql_connect()
    def delete_movie(self, movieid):
        """Delete a movie from database"""
        query = 'DELETE FROM VideoLibMovies WHERE MovieID = ?'
        self._execute_query(query, (movieid,))

    @db_base.sql_connect()
    def delete_tvshow(self, tvshowid):
        """Delete a tvshow from database"""
        query = 'DELETE FROM VideoLibTvShows WHERE TvShowID = ?'
        self._execute_query(query, (tvshowid,))

    @db_base.sql_connect()
    def delete_season(self, tvshowid, seasonid):
        """Delete a season from database"""
        query = 'DELETE FROM VideoLibSeasons WHERE TvShowID = ?, SeasonID = ?'
        self._execute_query(query, (tvshowid, seasonid))
        # if there are no other seasons, delete the tvshow
        query = 'SELECT EXISTS(FROM VideoLibSeasons WHERE TvShowID = ?)'
        cur = self._execute_query(query, (tvshowid,))
        if not bool(cur.fetchone()):
            self.delete_tvshow(tvshowid)

    @db_base.sql_connect()
    def delete_episode(self, tvshowid, seasonid, episodeid):
        """Delete a episode from database"""
        query = 'DELETE FROM VideoLibEpisodes WHERE SeasonID = ?, EpisodeID = ?'
        self._execute_query(query, (seasonid, episodeid))
        # if there are no other episodes, delete the season
        query = 'SELECT EXISTS(FROM VideoLibEpisodes WHERE SeasonID = ?)'
        cur = self._execute_query(query, (seasonid,))
        if not bool(cur.fetchone()):
            self.delete_season(tvshowid, seasonid)
