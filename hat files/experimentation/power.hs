module Main where

main :: IO ()

main = putStrLn (show (power 5 3))

power :: Integer -> Integer -> Integer

power b e = if e == 1 then b else b * (power b (e - 1))
