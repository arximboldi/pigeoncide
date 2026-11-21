import cProfile
import pstats

from main import pigeoncide_main

file_name = 'pigeoncide-profile'
cProfile.run ('pigeoncide_main ()', file_name)

stats = pstats.Stats (file_name)
#stats.sort_stats ('time')
stats.sort_stats ('cumulative')
stats.print_stats ()


