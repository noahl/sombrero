module Main where

main :: IO ()
main =
  let x = (False::Bool)
  in putStrLn (show (if x then (24::Int) else (42::Int)))
