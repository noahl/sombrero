module Main where

main :: IO ()
main = putStrLn (show (if True then (42::Int) else (24::Int)))
