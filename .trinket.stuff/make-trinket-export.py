#!/usr/bin/env python3

__doc__ = """Make a version of the python-visualizations that's easy to
export to trinket.io
"""

import argparse, sys, os, glob, shutil, re

specialContent = {
   'main.py': '''
from runAllVisualizationsMenu import *

showVisualizations(
    findVisualizations('.'),
    title='Algorithm Visualizations',
    adjustForTrinket=True)
'''
   }

if __name__ == '__main__':
   mustHave = ['VisualizationApp.py']
   replacements = [('▶', '=left_arrow='), ('▢', 'W'), ('✓', 'X')]
   parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument(
      'output_directory', nargs=1, help='Directory to put trinket export in')
   parser.add_argument(
      '-f', '--force', default=False, action='store_true',
      help='Clear directory if it already exists before exporting')
   parser.add_argument(
      '-x', '--exclude', nargs='*', default=['__init__.*', '.*[Tt]est.*'],
      help='Regex for filenames to exclude from export')
   parser.add_argument(
      '-v', '--verbose', action='count', default=0,
      help='Add verbose comments')
   args = parser.parse_args()
   
   outdir = args.output_directory[0]
   verbose = args.verbose
   exclude = [re.compile(exp) for exp in args.exclude]

   if not all(os.path.exists(f) for f in mustHave):
      print('Missing some files.  Expected to find: {}'.format(
         ', '.join(mustHave)))
      print('Is the current directory PythonVisualizations?')
      sys.exit(-1)
      
   if os.path.exists(outdir):
      if os.path.isdir(outdir) and args.force:
         if verbose > 0:
            print('Clearing {} directory'.format(outdir))
         shutil.rmtree(outdir)
         os.mkdir(outdir)
      elif os.path.isdir(outdir):
         print('{} exists.  Use --force option to clear contents first'.format(
            outdir))
         sys.exit(0)
      else:
         print('{} is not a directory.{}'.format(
            outdir, 'Ignoring --force' if args.force else ''))
         sys.exit(-1)
   else:
      if verbose > 0:
         print('Creating {} directory'.format(outdir))
      os.mkdir(outdir)

   files = glob.glob('*.py')
   for filename in files:
      if filename in specialContent:
         print('Skipping export of {}'.fomrat(filename))
         continue

      if any(regex.match(filename) for regex in exclude):
         if verbose > 0:
            print('Excluding {} for match to an exclude pattern'.format(
               filename))
         continue
      
      with open(filename, 'r') as infile:
         content = infile.read()
         revised = content
         for pair in replacements:
            revised = revised.replace(*pair)
         if verbose > 0:
            print('Exporting {}{}'.format(
               filename, ' with substitions' if content != revised else ''))
         with open(os.path.join(outdir, filename), 'w') as outfile:
            outfile.write(revised)
            outfile.close()

   for filename in specialContent:
      if verbose > 0:
         print('Creating {}'.format(filename))
      with open(os.path.join(outdir, filename), 'w') as outfile:
         outfile.write(specialContent[filename])
         outfile.close()
         
   print('Created export in {}'.format(outdir))
