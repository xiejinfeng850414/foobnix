#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util.fc import FC
from foobnix.util import LOG
from foobnix.regui.state import LoadSave
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.id3 import update_all_id3
import os
from foobnix.regui.model import FModel
from foobnix.regui.service.lastfm_service import LastFmService
from foobnix.util.singe_thread import SingreThread
from foobnix.regui.service.vk_service import VKService
class BaseFoobnixControls(LoadSave):
    def __init__(self):        
        self.lastfm = LastFmService()    
        self.vk = VKService()    
        pass
    
    def state_play(self):
        self.media_engine.state_play()
    
    def state_pause(self):
        self.media_engine.state_pause()
    
    def state_stop(self):
        self.media_engine.state_stop()
    
    def play(self, bean):
        if bean.path == None:
            vk = self.vk.find_one_track(bean.text)
            if vk:            
                bean.path = vk.path
                bean.time = vk.time
            else:
                self.next()
            
        self.media_engine.play(bean.path)
        print "!!!!!!", bean.info
        self.statusbar.set_text(bean.info)
    
    def notify_playing(self, pos_sec, dur_sec):
        self.seek_bar.update_seek_status(pos_sec, dur_sec)
    
    def notify_eos(self):
        self.next()
            
    def player_seek(self, percent):
        self.media_engine.seek(percent)
        
    def player_volue(self, percent):
        self.media_engine.volume(percent)
    
    def search_top_tracks(self, query):
        def inline(query):            
            results = self.lastfm.search_top_tracks(query)
            all = []
            for i, bean in enumerate(results):
                bean.tracknumber = i + 1
                all.append(bean)            
            self.notetabs.append_tab(query, all)        
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)
    
    def search_top_albums(self, query):
        def inline(query):
            results = self.lastfm.search_top_albums(query)
            self.notetabs.append_tab(query, None)
            for album in results[:5]:
                all = []
                album.add_font("bold")
                all.append(album)            
                tracks = self.lastfm.search_album_tracks(album.artist, album.album)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    all.append(track)
                self.notetabs.append(all)                
        #inline(query)        
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)
    
    def search_top_similar(self, query):
        def inline(query):            
            results = self.lastfm.search_top_similar_artist(query)
            self.notetabs.append_tab(query, None)
            for artist in results[:5]:
                all = []
                artist.add_font("bold")
                all.append(artist)            
                tracks = self.lastfm.search_top_tracks(artist.artist)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    all.append(track)
                self.notetabs.append(all)            
        #inline(query)         
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)
    
    def search_top_tags(self, query):
        def inline(query):            
            results = self.lastfm.search_top_tags(query)           
            self.notetabs.append_tab(query, None)
            for tag in results[:5]:
                all = []
                tag.add_font("bold")
                all.append(tag)            
                tracks = self.lastfm.search_top_tag_tracks(tag.text)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    all.append(track)
                self.notetabs.append(all)
        #inline(query)     
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)
    
    def search_all(self, query):
        pass
        def inline(query):            
            print query            
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)
   
    def update_info_panel(self, bean):
        #self.info_panel.update(bean)        
        self.singre_thread.run_with_text(self.info_panel.update, bean, "Updating info panel")        
        
    def append_to_notebook(self, text, beans):
        path = beans[0].path
        if os.path.isdir(path):
            scanner = DirectoryScanner(beans[0].path)
            results = scanner.get_music_file_results()
            results = update_all_id3(results)        
            self.notetabs.append_tab(text, results)
        else:
            self.notetabs.append_tab(text, [beans[0]])
                
    def ass(self, i):
        self.notetabs.append(FModel(i, "3").add_level(None))
        
    def next(self):
        bean = self.notetabs.next()
        self.play(bean)
    
    def prev(self):
        bean = self.notetabs.prev()
        self.media_engine.play(bean)
    
    def filter_tree(self, value):
        self.tree.filter(value)
    
    def quit(self, *a):
        LOG.info("Controls - Quit")
        self.on_save()
        FC().save()
        
        gtk.main_quit()
    
    
    def on_load(self):
        for element in self.__dict__:            
            if isinstance(self.__dict__[element], LoadSave):
                self.__dict__[element].on_load()
            else:
                LOG.debug("NOT LOAD", self.__dict__[element])
        self.singre_thread = SingreThread(self.search_progress)
        self.window.show()
            
    def on_save(self):
        for element in self.__dict__:
            if isinstance(self.__dict__[element], LoadSave):
                self.__dict__[element].on_save()
            else:
                LOG.debug("NOT SAVE", self.__dict__[element])