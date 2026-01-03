"""
Test file for extract_say_command function
Tests that messages are extracted without truncation
"""

from reflection import extract_say_command

def test_extract_say_command():
    """Test various message formats to ensure no truncation"""
    
    print("=" * 80)
    print("TESTING extract_say_command()")
    print("=" * 80)
    
    # Test 1: Message with apostrophes
    test1 = """Problem: Students are spending too long discussing homework.
Solution: 1. Have Professor say "Let's move on to the next topic now"
"""
    result1 = extract_say_command(test1)
    expected1 = '1. Have Professor say "Let\'s move on to the next topic now"'
    print(f"\n✓ Test 1: Apostrophes")
    print(f"  Input: {test1[:80]}...")
    print(f"  Expected: {expected1}")
    print(f"  Got:      {result1}")
    print(f"  PASS: {result1 == expected1}")
    
    # Test 2: Long message with multiple apostrophes
    test2 = """Problem: Coach is not addressing concerns.
Solution: 1. Have Martinez say "I've heard everyone's concerns. Let me announce our modified practice schedule for finals week that accommodates both tennis training and your academic needs."
"""
    result2 = extract_say_command(test2)
    expected2 = '1. Have Martinez say "I\'ve heard everyone\'s concerns. Let me announce our modified practice schedule for finals week that accommodates both tennis training and your academic needs."'
    print(f"\n✓ Test 2: Long message with apostrophes")
    print(f"  Input: {test2[:80]}...")
    print(f"  Expected: {expected2}")
    print(f"  Got:      {result2}")
    print(f"  PASS: {result2 == expected2}")
    
    # Test 3: Multiple solution steps
    test3 = """Problem: Agents are not interacting.
Solution: 1. Move Professor to classroom
          2. Have Professor say "Class is starting now"
          3. Have Bob say "I'm ready to begin"
"""
    result3 = extract_say_command(test3)
    expected3 = """1. Move Professor to classroom
          2. Have Professor say "Class is starting now"
          3. Have Bob say "I'm ready to begin\""""
    print(f"\n✓ Test 3: Multiple solution steps")
    print(f"  Input: {test3[:80]}...")
    print(f"  Expected: {expected3[:80]}...")
    print(f"  Got:      {result3[:80]}...")
    print(f"  PASS: {result3 == expected3}")
    
    # Test 4: Message with quotes inside quotes
    test4 = """Problem: X
Solution: 1. Have Coach say "I heard you say 'we need more time' but we can't extend the deadline"
"""
    result4 = extract_say_command(test4)
    expected4 = '1. Have Coach say "I heard you say \'we need more time\' but we can\'t extend the deadline"'
    print(f"\n✓ Test 4: Nested quotes")
    print(f"  Input: {test4[:80]}...")
    print(f"  Expected: {expected4}")
    print(f"  Got:      {result4}")
    print(f"  PASS: {result4 == expected4}")
    
    # Test 5: Empty/smooth simulation
    test5 = "Simulation is running smoothly."
    result5 = extract_say_command(test5)
    expected5 = ""
    print(f"\n✓ Test 5: Running smoothly")
    print(f"  Input: {test5}")
    print(f"  Expected: (empty string)")
    print(f"  Got:      {result5}")
    print(f"  PASS: {result5 == expected5}")
    
    # Test 6: No Solution: keyword
    test6 = "Problem: Something is wrong but no solution provided"
    result6 = extract_say_command(test6)
    expected6 = ""
    print(f"\n✓ Test 6: No Solution keyword")
    print(f"  Input: {test6}")
    print(f"  Expected: (empty string)")
    print(f"  Got:      {result6}")
    print(f"  PASS: {result6 == expected6}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_extract_say_command()
