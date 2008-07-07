module Main where

main :: IO ()
main = putStrLn (show (increase (30::Int)))

increase :: Int -> Int
increase x = x + 12
